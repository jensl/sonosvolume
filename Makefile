all: build-ui copy-ui

build-ui:
	git submodule update --init ui && \
	cd ui && \
	if [ -z "$$SKIP_NPM_INSTALL" ]; then npm install; fi && \
	npm run build

copy-ui:
	git rm -rf --quiet sonosvolume/static-ui 2>/dev/null ; \
	rm -rf sonosvolume/static-ui && \
	cp -r ui/build sonosvolume/static-ui && \
	git add sonosvolume/static-ui
