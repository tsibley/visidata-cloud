SHELL := /bin/bash -euo pipefail

vendored_node_modules := \
	node_modules/xterm/lib/xterm.js \
	node_modules/xterm/css/xterm.css \
	node_modules/xterm-addon-attach/lib/xterm-addon-attach.js \
	node_modules/xterm-addon-fit/lib/xterm-addon-fit.js

build: build-image build-frontend

build-image:
	docker build -t visidata .

build-frontend:
	npm ci
	cp -v $(vendored_node_modules) vendor/
