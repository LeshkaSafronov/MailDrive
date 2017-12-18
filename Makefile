SHELL := /bin/bash

.PHONY: install-docker
install-docker:
	sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
	sudo apt-add-repository 'deb https://apt.dockerproject.org/repo ubuntu-xenial main'
	sudo apt-get update
	sudo apt-get install -y docker-engine


.PHONY: install-docker-compose
install-docker-compose:
	sudo curl -L https://github.com/docker/compose/releases/download/1.17.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
	sudo chmod +x /usr/local/bin/docker-compose


.PHONY: setup-environment
setup-environment: install-docker install-docker-compose


.PHONY: build-python
build-python:
	docker build -t python python/

.PHONY: build-ui
build-ui:
	docker build -t ui ui/
	docker run \
		-it \
		--volume ${PWD}/nginx/ui:/uibuild \
		ui \
		/bin/bash -c "npm install && npm run build && cp -r /source/build/* /uibuild"


.PHONY: build-nginx
build-nginx: build-ui
	docker build -t nginx-ui nginx/

.PHONY: build-db
build-db:
	docker build -t db db/

.PHONY: up
up: build-db build-python build-nginx
	if ! docker network ls | awk '{ print $$2 }' | grep proxy-nginx; \
		then \
			docker network create proxy-nginx; \
	fi;
	docker-compose up

.PHONY: up-backend
up-backend: build-db build-python
	if ! docker network ls | awk '{ print $$2 }' | grep proxy-nginx; \
		then \
			docker network create proxy-nginx; \
	fi;
	docker-compose up

.PHONY: down
down:
	docker-compose down --remove-orphans

.PHONY: restart
restart: down up

.PHONY: down-test
down-test:
	docker-compose down -v --remove-orphans

.PHONY: up-test
test: build-db build-python
	docker-compose -f docker-compose-tests.yml up

.PHONY: restart-test
restart-test: down-test test

.PHONY: clean
clean:
	docker-compose down;
	if [[ $$(docker container ls -a -q) ]]; \
		then \
			docker rm $$(docker container ls -a -q); \
	fi;
	if [[ $$(docker volume ls -q) ]]; \
		then \
			docker volume rm $$(docker volume ls -q); \
	fi;
