import os

CONNECTION_STRING = "host='{db_host}' " \
                    "dbname='{db_name}'" \
                    "user='{db_user}'" \
                    "password='{db_password}'".format(db_host=os.environ['DB_HOST'],
                                                      db_name=os.environ['DB_NAME'],
                                                      db_user=os.environ['DB_USER'],
                                                      db_password=os.environ['DB_PASSWORD'])

MINIO_HOST = os.environ['MINIO_HOST']
MINIO_PORT = os.environ['MINIO_PORT']

MINIO_ACCESS_KEY = os.environ['MINIO_ACCESS_KEY']
MINIO_SECRET_KEY = os.environ['MINIO_SECRET_KEY']