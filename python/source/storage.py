import boto3
import botocore
import settings
import logging

from functools import lru_cache


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
            logging.warning(client.list_buckets())
        except botocore.vendored.requests.exceptions.ConnectionError as e:
            logging.warning('Cannot connect to {}. Reason {}'.format(
                '{}:{}'.format(settings.MINIO_HOST,
                               settings.MINIO_PORT),
                str(e))
            )
        else:
            logging.warning('Connection to minio successed!!!')
            break
    return client


client = init_client()