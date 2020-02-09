SHELL := /bin/bash -euo pipefail

subdirs := backend container frontend

all: $(subdirs)

$(subdirs):
	$(MAKE) -C $@

.PHONY: all $(subdirs)
