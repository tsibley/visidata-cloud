# VisiData Cloud

Fully-functional [VisiData](https://visidata.org) sessions in your browser.

* Access from any device
* Sessions persist until you quit VisiData
* Live sharing of sessions by sharing the link

To come?

* Drag-and-drop local files
* Dataset pre-loading and command pre-play via URL, e.g. "browse in VisiData" links
* Copy/paste integration
* View-only sharing of sessions
* Recorded sessions / batch command logs
* Suspend/resume of sessions


## Development

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

If you run into trouble with Docker, first make sure your Docker host/daemon
is working by running `docker run hello-world`.


## Todo

### Features

See above, with some more thoughts below.

  * Supporting natural copy/paste will be tricky.
    - vd configured with helper clipboard commands
    - container ⇄ browser in-band signaling using custom escape codes (or a
      side-channel)
    - keyboard shortcuts? xterm currently binds paste to Shift-Insert, but
      this isn't natural.

  * Drag-and-drop of local files
    - Upload file from browser to backend, into temporary storage shared by
      backend and container (either local or remote, like, S3).
    - Trigger vd macro or input strings to load that file as a new sheet, e.g. `Esc`, `Esc`, `space`, `open-file`, `Enter`, `<path/url>`, `Enter`.

### Bugs

A very partial list of problems I've noticed.

  * Mouse scrolling works one direction but not the other
  * Right click opens browser context menu
  * [Shift-]Ctrl-{N,T,W} cannot be captured. :-(  The biggest frustration here
    is that Ctrl-W normally scrubs the last word when editing text in the
    terminal, but in a browser closes the tab/window.
  * Terminal size handling when resizing the browser window
  * Terminal size handling when sharing a session

### Security

Lots to do here on the Docker side before making this generally available.  A
very much partial list of thoughts.

  * Further limits on container resources
  * Limits on total container run time
  * Container network isolation
  * Container network egress/ingress restrictions
  * Container host-access restrictions
  * Origin validation for WebSocket connections

### Administration

  * Automatically pause and unpause containers on page unload/load
  * Reap containers over a certain idle age
