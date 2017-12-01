#!/usr/bin/env bash
set -e

export DB_HOST=db-test
export DB_NAME=mail_drive
export DB_USER=leshka
export DB_PASSWORD=leshka

export MINIO_HOST=minio1-test
export MINIO_PORT=9000
export MINIO_ACCESS_KEY=set-value-here
export MINIO_SECRET_KEY=set-value-here

python3.5 wait_postgres.py pg_database
python3.5 server.py