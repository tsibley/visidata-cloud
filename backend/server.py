"""
VisiData Cloud web backend.

The ``/containers/…`` endpoints surficially mimic the Docker Engine API in
order to take advantage of an existing API design instead of bikeshedding my
own.  (This was also handy because my initial prototypes used direct access to
the Docker Engine API, but that's untenable from a security standpoint.)
"""
from starlette.applications import Starlette
from starlette.routing import Mount, WebSocketRoute

from routing import Get, Post
from endpoints import *


routes = [
    Get("/", index),
    Get("/vd", vd),
    Post("/containers/create", create_container),
    Post("/containers/{id:container}/start", start_container),
    Post("/containers/{id:container}/resize", resize_container_tty),
    WebSocketRoute("/containers/{id:container}/attach/ws", attach_to_container),
    Mount("/", frontend_public)]


app = Starlette(routes = routes)
