.PHONY: build dev clean install test test-unit test-browser install-browser

install:
	pip install -r requirements.txt

build:
	python sources/build.py

dev:
	nohup python dev/server.py &

test: test-unit test-browser

test-unit:
	python -m pytest

test-browser:
	npm run test:browser

install-browser:
	npx playwright install

clean:
	rm -rf fonts/variable/* fonts/ttf/* fonts/webfonts/*
