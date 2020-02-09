# VisiData Cloud

Fully-functional [VisiData](https://visidata.org) sessions in your browser.

* Access from any device
* Real-time shared sessions with link-sharing

To come:

* Drag-and-drop local files
* Copy/paste integration
* Persistent sessions


## Run your own

VisiData Cloud is comprised of the following components:

* A backend web server written in Python
* A frontend web client written in JavaScript
* A Docker container image for running VisiData
* A Docker host for running containers

First, make sure the following are installed:

* Python 3.8
* [Pipenv](https://pipenv.readthedocs.io)
* npm
* Docker

Then, run `make` to install the backend deps and build the container.

Finally, run `./backend/run` to start the backend server.

Visit [http://localhost:8000](http://localhost:8000).

If you want to run containers on a different host, set the standard
`DOCKER_HOST` environment variable.
