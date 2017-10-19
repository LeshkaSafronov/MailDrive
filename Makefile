.PHONY: python
python:
	docker build -t python python/

.PHONY: up
up: python
	docker-compose up
