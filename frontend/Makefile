SHELL := /bin/bash -euo pipefail


build:
	# noop


vendored_node_modules := \
	node_modules/xterm/lib/xterm.js \
	node_modules/xterm/lib/xterm.js.map \
	node_modules/xterm/css/xterm.css \
	node_modules/xterm-addon-attach/lib/xterm-addon-attach.js \
	node_modules/xterm-addon-attach/lib/xterm-addon-attach.js.map \
	node_modules/xterm-addon-fit/lib/xterm-addon-fit.js \
	node_modules/xterm-addon-fit/lib/xterm-addon-fit.js.map

vendor:
	npm ci
	mkdir -p vendor
	cp -v $(vendored_node_modules) vendor/
	rm -rf node_modules

.PHONY: vendor
