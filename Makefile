SHELL := /bin/bash -euo pipefail

build: build-image build-frontend

build-image:
	docker build -t visidata .

build-frontend:
	npm ci
