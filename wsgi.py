"""
RESTful web API for VisiData Cloud's backend.

The ``/containers/…`` endpoints surficially mimic the Docker Engine API in
order to take advantage of an existing API design instead of bikeshedding my
own.  (My initial prototypes also used direct access to the Docker Engine API,
but that's untenable from a security standpoint.)
"""
from docker import DockerClient, errors as DockerError
from flask import Flask, request, send_file, send_from_directory
from os import environ


VISIDATA_IMAGE = environ.get("VISIDATA_IMAGE") or "visidata"


docker = DockerClient.from_env()
app = Flask(__name__)


@app.route("/vd", methods = ["GET"])
def vd():
    return send_file("vd.html", "text/html; charset=UTF-8")


@app.route("/vendor/<path:filename>", methods = ["GET"])
def vendor(filename):
    return send_from_directory("vendor", filename)


@app.route("/containers/create", methods = ["POST"])
def api_containers_create():
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


if __name__ == "__main__":
    app.run(debug=True)
