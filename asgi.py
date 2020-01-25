"""
RESTful web API for VisiData Cloud's backend.

The ``/containers/…`` endpoints surficially mimic the Docker Engine API in
order to take advantage of an existing API design instead of bikeshedding my
own.  (My initial prototypes also used direct access to the Docker Engine API,
but that's untenable from a security standpoint.)
"""
from docker import DockerClient, errors as DockerError
from starlette.applications import Starlette
from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles
from os import environ


VISIDATA_IMAGE = environ.get("VISIDATA_IMAGE") or "visidata"


docker = DockerClient.from_env()


def vd(request):
    return send_file("vd.html", "text/html; charset=UTF-8")


def containers_create(request):
    container = docker.containers.create(
        VISIDATA_IMAGE,
        auto_remove = True,
        detach      = True,
        init        = True,
        tty         = True,
        stdin_open  = True)

    return {"Id": container.id}, 200


# XXX TODO: use app.url_map to make this <container:id> and do the .get() + 404
# handling for us
#    <https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.url_map>

@app.route("/containers/<container_id>/start", methods = ["POST"])
def api_containers_start(container_id):
    try:
        container = docker.containers.get(container_id)
    except DockerError.NotFound as error:
        return {"message": error.explanation}, 404

    container.start()
    return "", 204


@app.route("/containers/<container_id>/resize", methods = ["POST"])
def api_containers_resize(container_id):
    h = request.args.get("h")
    w = request.args.get("w")

    try:
        container = docker.containers.get(container_id)
    except DockerError.NotFound as error:
        return {"message": error.explanation}, 404

    container.resize(h, w)
    return "", 204


@app.route("/containers/<container_id>/attach/ws", methods = ["POST"])
def api_containers_attach_ws(container_id):
    ...
    # XXX: redirect to ws proxy?


routes = [
    Route("/vd", vd),
    Mount("/vendor", StaticFiles(directory = "vendor")),
    Route("/containers/create", containers_create, methods = ["POST"]),
]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
