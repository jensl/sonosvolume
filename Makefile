all: build-ui copy-ui

build-ui:
	git submodule update --init ui && \
	cd ui && \
	npm install && \
	npm run build

copy-ui:
	git rm -r sonosvolume/static-ui && \
	cp -r ui/build sonosvolume/static-ui && \
	git add sonosvolume/static-ui
