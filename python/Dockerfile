FROM python:3.5
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

ADD requirements.txt /code/

RUN pip install -r requirements.txt

ADD source /code/
ADD source/tests /code/

ADD entrypoint.sh /
ADD test-entrypoint.sh /