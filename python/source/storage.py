import boto3
import botocore
import settings
import logging

from functools import lru_cache
from botocore.exceptions import ClientError


@lru_cache(maxsize=2)
def init_client():
    client = boto3.client(
        service_name='s3',
        region_name='us-east-1',
        use_ssl=False,
        endpoint_url='http://{}:{}'.format(settings.MINIO_HOST, settings.MINIO_PORT),
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        config=botocore.client.Config(signature_version='s3v4')
    )
    while True:
        try:
            client.list_buckets()
        except ClientError as e:
            logging.warning('Cannot connect to {}. Reason {}'.format(
                '{}:{}'.format(settings.MINIO_HOST,
                               settings.MINIO_PORT),
                str(e))
            )
        else:
            logging.warning('Connection to minio successed!!!')
            break

    try:
        client.head_bucket(Bucket='users')
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            client.create_bucket(Bucket = 'users')

    return client


client = init_client()