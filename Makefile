.PHONY: build dev clean install

install:
	pip install -r requirements.txt

build:
	python src/build.py

dev:
	nohup python dev/server.py &

clean:
	rm -rf fonts/*.ttf fonts/*.woff2
