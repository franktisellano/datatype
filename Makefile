.PHONY: build dev clean install

install:
	pip install -r requirements.txt

build:
	python sources/build.py

dev:
	nohup python dev/server.py &

clean:
	rm -rf fonts/variable/* fonts/ttf/* fonts/webfonts/*
