#!/usr/bin/env bash
set -e

python3.6 manage.py migrate
python3.6 manage.py runserver 0.0.0.0:8000

