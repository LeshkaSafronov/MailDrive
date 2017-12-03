import requests
import logging
import time

from tests_settings import ENDPOINT


def wait_web():
    while True:
        try:
            requests.get(ENDPOINT)
        except requests.exceptions.ConnectionError as e:
            logging.warning('Cound not connect to {}. Reason {}'.format(ENDPOINT, str(e)))
        else:
            break
        time.sleep(1)


if __name__ == '__main__':
    wait_web()