.PHONY: python
python:
	docker build -t python python/

.PHONY: db
db:
	docker build -t db db/

.PHONY: up
up: db python
	docker-compose up

.PHONY: down
down:
	docker-compose down

.PHONY: restart
restart: down up