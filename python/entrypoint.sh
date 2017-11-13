#!/usr/bin/env bash
set -e

python3.5 wait_postgres.py pg_database
python3.5 init_db.py
