"""
RESTful web API for VisiData Cloud's backend.

The ``/containers/…`` endpoints surficially mimic the Docker Engine API in
order to take advantage of an existing API design instead of bikeshedding my
own.  (My initial prototypes also used direct access to the Docker Engine API,
but that's untenable from a security standpoint.)
"""
import asyncio
import websockets
from docker import DockerClient, errors as DockerError
from functools import partial
from pathlib import Path
from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.responses import FileResponse, JSONResponse, PlainTextResponse
from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles
from os import environ


VISIDATA_IMAGE = environ.get("VISIDATA_IMAGE") or "visidata"

root = Path(__file__).parent
docker = DockerClient.from_env()


def vd(request):
    return FileResponse(root / "vd.html")


def create_container(request):
    container = docker.containers.create(
        VISIDATA_IMAGE,
        auto_remove = True,
        detach      = True,
        init        = True,
        tty         = True,
        stdin_open  = True)

    return JSONResponse({"Id": container.id})


def start_container(request):
    id = request.path_params["id"]

    try:
        container = docker.containers.get(id)
    except DockerError.NotFound as error:
        return JSONResponse({"message": error.explanation}, 404)

    container.start()

    return PlainTextResponse("", 204)


def resize_container_tty(request):
    id = request.path_params["id"]
    h  = request.query_params.get("h")
    w  = request.query_params.get("w")

    try:
        container = docker.containers.get(id)
    except DockerError.NotFound as error:
        return JSONResponse({"message": error.explanation}, 404)

    container.resize(h, w)

    return PlainTextResponse("", 204)


class attach_to_container(WebSocketEndpoint):
    docker_socket = None
    docker_receive = None

    async def on_connect(self, browser_socket):
        # XXX FIXME: docker.api.base_url
        # do a bit of munging from http[s]://localhost/… → connect("ws[s]://localhost/…")
        # do a bit of munging from http[s]+unix://localhost/… → unix_connect(…path…, "ws[s]://localhost/…")

        # Connect to the container
        id = browser_socket.path_params["id"]
        url = str(browser_socket.url.replace(scheme = "ws", netloc = "localhost:8080"))

        try:
            self.docker_socket = await websockets.connect(url)
        except websockets.exceptions.InvalidStatusCode as error:
            # XXX FIXME
            #return PlainTextResponse("", error.status_code)
            await browser_socket.close()

        await browser_socket.accept()

        async def docker_receive():
            # Forward data from the container to the browser.
            async for data in self.docker_socket:
                if isinstance(data, bytes):
                    await browser_socket.send_bytes(data)
                elif isinstance(data, str):
                    await browser_socket.send_text(data)
                else:
                    raise Exception("websocket frame from docker socket is not bytes or str but {type(data).__name__}")

        self.docker_receive = asyncio.create_task(docker_receive())

    async def on_receive(self, browser_socket, data):
        # Forward data from the browser to the container.
        try:
            await self.docker_socket.send(data)
        except websockets.exceptions.ConnectionClosed:
            await browser_socket.close()

    async def on_disconnect(self, browser_socket, close_code):
        if self.docker_receive:
            self.docker_receive.cancel()

        if self.docker_socket:
            await self.docker_socket.close()


Get  = partial(Route, methods = ["GET"])
Post = partial(Route, methods = ["POST"])

routes = [
    Get("/vd", vd),
    Post("/containers/create", create_container),
    Post("/containers/{id}/start", start_container),
    Post("/containers/{id}/resize", resize_container_tty),
    WebSocketRoute("/containers/{id}/attach/ws", attach_to_container),
    Mount("/vendor", StaticFiles(directory = root / "vendor")),
]

app = Starlette(routes = routes)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
