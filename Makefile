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

.PHONY: build-ui
build-ui:
	docker build -t ui ui/
	docker run \
	    -it \
	    --volume ${PWD}/nginx/ui:/uibuild \
	    ui \
	    /bin/bash -c "npm install && npm run build && cp -r /source/build/* /uibuild"

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