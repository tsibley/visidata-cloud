SHELL := /bin/bash -euo pipefail


build: build-image build-frontend


build-image:
	docker build -t visidata .


vendored_node_modules := \
	node_modules/xterm/lib/xterm.js \
	node_modules/xterm/css/xterm.css \
	node_modules/xterm-addon-attach/lib/xterm-addon-attach.js \
	node_modules/xterm-addon-fit/lib/xterm-addon-fit.js

build-frontend:
	npm ci
	cp -v $(vendored_node_modules) vendor/
	rm -rf node_modules
