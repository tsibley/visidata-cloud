"""
VisiData Cloud backend.

The ``/containers/…`` endpoints surficially mimic the Docker Engine API in
order to take advantage of an existing API design instead of bikeshedding my
own.  (This was also handy because my initial prototypes used direct access to
the Docker Engine API, but that's untenable from a security standpoint.)
"""
import asyncio
import logging
import re
import websockets
from docker import DockerClient, errors as DockerError
from docker.utils import parse_host as parse_docker_host
from functools import partial
from os import environ
from pathlib import Path
from starlette.applications import Starlette
from starlette.responses import FileResponse, JSONResponse, PlainTextResponse
from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocketState
from urllib.parse import urlsplit, urlunsplit


VISIDATA_IMAGE = environ.get("VISIDATA_IMAGE") or "visidata"

DOCKER_HOST = urlsplit(parse_docker_host(environ.get("DOCKER_HOST")))

assert DOCKER_HOST.scheme in {"http", "https", "http+unix"}, \
    f"DOCKER_HOST={DOCKER_HOST!r} uses an unsupported scheme"


frontend = Path(__file__).parent.parent / "frontend"
assert frontend.is_dir()

docker = DockerClient.from_env()
logger = logging.getLogger(__name__)
logging.basicConfig()


def vd(request):
    return FileResponse(frontend / "vd.html")


def create_container(request):
    container = docker.containers.create(
        VISIDATA_IMAGE,
        command       = ["--quitguard"],
        init          = True,
        detach        = True,
        auto_remove   = True,
        tty           = True,
        stdin_open    = True,

        # 100MB of RAM, no swap
        mem_limit     = "100m",
        memswap_limit = "100m",

        # Equivalent to half a CPU, e.g. --cpus 0.5.  See
        # <https://docs.docker.com/config/containers/resource_constraints/#configure-the-default-cfs-scheduler>.
        cpu_period    = 100000,
        cpu_quota     =  50000,

        # Read-only root filesystem with homedir as writeable 100MB tmpfs
        read_only     = True,
        tmpfs         = {"/home/visidata": "rw,size=100m,mode=1700,uid=1000"})

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


async def attach_to_container(browser_socket):
    # XXX TODO: Do origin checking?

    # browser_socket is a starlette.websockets.WebSocket object
    # container_socket is a websockets.client.WebSocketClientProtocol object

    # Figure out the Docker API ws[s]:// URL to connect to
    id = browser_socket.path_params["id"]
    query = browser_socket.url.query

    attach_url = urlunsplit((
        {"http": "ws", "https": "wss", "http+unix": "ws"}[DOCKER_HOST.scheme],
        DOCKER_HOST.netloc or "localhost",
        f"/v1.40/containers/{id}/attach/ws",
        query,
        None
    ))

    if DOCKER_HOST.scheme == "http+unix":
        container_connection = websockets.unix_connect(DOCKER_HOST.path, attach_url)
    else:
        container_connection = websockets.connect(attach_url)

    # Connect to the Docker API websocket endpoint
    try:
        log("container.attaching", container = id, url = attach_url)
        container_socket = await container_connection
    except websockets.exceptions.WebSocketException as error:
        log("container.attach-failed", container = id, error = error)
        return await browser_socket.close()

    try:
        await browser_socket.accept()

        # Coroutines to ferry data between the two sockets.
        async def browser_to_container():
            while True:
                message = await browser_socket.receive()

                # receive() updates client_state immediately based on the message.
                if browser_socket.client_state != WebSocketState.CONNECTED:
                    break

                if "bytes" in message:
                    await container_socket.send(message["bytes"])
                elif "text" in message:
                    await container_socket.send(message["text"])
                else:
                    raise RuntimeError(f"expected a 'bytes' or 'text' key in message: {message!r}")

        async def container_to_browser():
            async for data in container_socket:
                if isinstance(data, bytes):
                    await browser_socket.send_bytes(data)
                elif isinstance(data, str):
                    await browser_socket.send_text(data)
                else:
                    raise RuntimeError(f"expected a message of type bytes or str but got {type(data).__name__!r}")

        # Run coroutines concurrently until one of them exits.
        tasks = [
            asyncio.create_task(browser_to_container()),
            asyncio.create_task(container_to_browser())]

        done, pending = await asyncio.wait(tasks, return_when = asyncio.FIRST_COMPLETED)

        for task in pending:
            task.cancel()
    finally:
        await container_socket.close()
        await browser_socket.close()


def log(msg, **data):
    failed = re.compile(r"(^|\b)failed(\b|$)")
    level = "error" if failed.search(msg) else "info"
    getattr(logger, level)({
        **data,
        "msg": f"backend.{msg}",
        "DOCKER_HOST": DOCKER_HOST.geturl(),
        "VISIDATA_IMAGE": VISIDATA_IMAGE,
    })


Get  = partial(Route, methods = ["GET"])
Post = partial(Route, methods = ["POST"])

routes = [
    Get("/", index),
    Get("/vd", vd),
    Post("/containers/create", create_container),
    Post("/containers/{id}/start", start_container),
    Post("/containers/{id}/resize", resize_container_tty),
    WebSocketRoute("/containers/{id}/attach/ws", attach_to_container),
    Mount("/assets", StaticFiles(directory = frontend / "assets"))]

app = Starlette(routes = routes)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
