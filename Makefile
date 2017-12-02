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
	docker-compose down --remove-orphans

.PHONY: down-test
down-test:
	docker-compose down -v --remove-orphans

.PHONY: restart
restart: down up

.PHONY: test
test: db python
	docker-compose -f docker-compose-tests.yml up

.PHONY: restart-test
restart-test: down-test test