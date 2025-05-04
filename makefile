.PHONY: build push

build:
	docker build -t habibmy/orderparser:latest .

push:
	docker push habibmy/orderparser:latest