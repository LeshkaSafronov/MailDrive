import os
import unittest
import settings
import psycopg2
import psycopg2.extras
import logging
import db
import json
from botocore.exceptions import ClientError

import requests
import time
from storage import client


WEB_HOST = os.environ['WEB_HOST']
WEB_PORT = os.environ['WEB_PORT']

ENDPOINT = 'http://{}:{}'.format(WEB_HOST, WEB_PORT)

IMAGE_DATA_1 = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07tIME\x07\xe1\x0c\x02\r:1\x02\x9a\n\x1d\x00\x00\x00\x19tEXtComment\x00Created with GIMPW\x81\x0e\x17\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82'
IMAGE_DATA_2 = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x02\x08\x02\x00\x00\x00\x16\xe3!p\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07tIME\x07\xe1\x0c\x02\x0f\x0c\x16-\x08\xfam\x00\x00\x00\x19tEXtComment\x00Created with GIMPW\x81\x0e\x17\x00\x00\x00\x10IDAT\x08\xd7c\xf8\xff\xff?\x13\x03\x03\x03\x00\x11\xfe\x03\x00\xf7\xaa\x99O\x00\x00\x00\x00IEND\xaeB`\x82'


def wait_web():
    while True:
        try:
            requests.get(ENDPOINT)
        except requests.exceptions.ConnectionError as e:
            logging.warning('Cound not connect to {}. Reason {}'.format(ENDPOINT, str(e)))
        else:
            break
        time.sleep(1)


class TestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_tables = ['mail_user']

    def erase_db(self):
        with psycopg2.connect(settings.CONNECTION_STRING) as conn:
            with conn.cursor() as cursor:
                for db_table in self.db_tables:
                    cursor.execute('TRUNCATE {};'.format(db_table))

    def add_db_user(self, data):
        with psycopg2.connect(settings.CONNECTION_STRING) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    db.build_universal_insert_query(
                        'mail_user',
                        fields=data.keys(),
                        values=data.values()
                    )
                )
                return cursor.fetchone()

    def list_db_user(self):
        with psycopg2.connect(settings.CONNECTION_STRING) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    db.build_universal_select_query('mail_user')
                )
                return cursor.fetchall()

    def setUp(self):
        self.erase_db()

        self.superadmin = self.add_db_user(
            {
                'email': 'superadmin',
                'password': 'superadmin'
            }
        )

        self.user_1 = self.add_db_user(
            {
                'name': 'Alexey',
                'subname': 'Safronov',
                'age': 20,
                'country': 'Mogilev',
                'telephone_number': '222322',
                'email': 'diamond.alex97@gmail.com',
                'password': '123',
                'avatar': '',
                'avatar_token': ''
            }
        )

        self.user_2 = self.add_db_user(
            {
                'name': 'Vlad',
                'subname': 'Punko',
                'age': 20,
                'country': 'Brest',
                'telephone_number': '345345345',
                'email': 'punko.kek@vlad.com',
                'password': '2345',
                'avatar': '',
                'avatar_token': ''
            }
        )

        self.user_3 = self.add_db_user(
            {
                'name': 'Jenya',
                'subname': 'Gusakovskaya',
                'age': 20,
                'country': 'Baranovichi',
                'telephone_number': '097654',
                'email': 'gusakovskaya.jenya@kek.com',
                'password': '657',
                'avatar': '',
                'avatar_token': ''
            }
        )

    def test_basic_auth(self):
        resp_without_auth = requests.get(os.path.join(ENDPOINT, 'api'))
        self.assertEqual(resp_without_auth.status_code, 401)

        resp = requests.get(
            os.path.join(ENDPOINT, 'api'),
            auth=('superadmin', 'superadmin')
        )
        self.assertEqual(resp.status_code, 200)

    def test_auth_via_session(self):
        with requests.session() as session:
            resp = session.get(os.path.join(ENDPOINT, 'api'))
            self.assertEqual(resp.status_code, 401)

            resp = session.post(
                os.path.join(ENDPOINT, 'api/users/login'),
                data=json.dumps(
                    {
                        'email': 'diamond.alex97@gmail.com',
                        'password': '123'
                    }
                )
            )
            self.assertEqual(resp.status_code, 200)

            resp = session.get(os.path.join(ENDPOINT, 'api'))
            self.assertEqual(resp.status_code, 200)

    def test_wrong_basic_auth(self):
        resp = requests.get(ENDPOINT, auth=('superadmin', 'kek'))
        self.assertEqual(resp.status_code, 401)

    def test_wrong_json_auth(self):
        resp = requests.post(
            os.path.join(ENDPOINT, 'api/users/login'),
            data=json.dumps(
                {
                    'email': 'diamond.alex97@gmail.com',
                    'password': '1234'
                }
            )
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.text, 'Invalide email or password')

    def test_not_existed_user(self):
        for method in ['get', 'put', 'delete']:
            resp = requests.request(
                method,
                os.path.join(ENDPOINT, 'api/users/0'),
                auth=('superadmin', 'superadmin')
            )
            self.assertEqual(resp.status_code, 404)
            self.assertEqual(resp.text, 'Not found')

        for method in ['get', 'put']:
            resp = requests.request(
                method,
                os.path.join(ENDPOINT, 'api/users/0/avatar'),
                auth=('superadmin', 'superadmin')
            )
            self.assertEqual(resp.status_code, 404)
            self.assertEqual(resp.text, 'Not found')

    def test_list_users(self):
        resp = requests.get(
            os.path.join(ENDPOINT, 'api/users'),
            auth=('superadmin', 'superadmin')
        )
        data = json.loads(resp.text)

        for response, user in zip(data, [self.superadmin, self.user_1, self.user_2, self.user_3]):
            for key, value in user.items():
                self.assertEqual(response[key], value)

    def test_get_user(self):
        resp = requests.get(
            os.path.join(ENDPOINT, 'api/users/{}'.format(self.user_2['id'])),
            auth=('superadmin', 'superadmin')
        )

        self.assertEqual(resp.status_code, 200)

        data = json.loads(resp.text)
        for key, value in self.user_2.items():
            self.assertEqual(data[key], value)

    def test_create_user(self):
        user_data = {
            'name': 'Jenya',
            'subname': 'Gusakovskaya',
            'age': 19,
            'country': 'Brest',
            'telephone_number': '03958784',
            'email': 'ololo.jeka@kek.com',
            'password': '345345'
        }

        resp = requests.post(
            os.path.join(ENDPOINT, 'api/users'),
            data=json.dumps(user_data),
            auth=('superadmin', 'superadmin')
        )

        self.assertEqual(resp.status_code, 201)

        data = json.loads(resp.text)
        for key, value in user_data.items():
            self.assertEqual(data[key], value)

        resp = requests.get(
            os.path.join(ENDPOINT, 'api/users'),
            auth=('superadmin', 'superadmin')
        )

        data = json.loads(resp.text)
        self.assertEqual(len(data), len(self.list_db_user()))

    def test_create_user_without_email(self):
        user_data = {
            'name': 'Jenya',
            'subname': 'Gusakovskaya',
            'age': 19,
            'country': 'Brest',
            'telephone_number': '03958784',
            'password': '345345'
        }

        resp = requests.post(
            os.path.join(ENDPOINT, 'api/users'),
            data=json.dumps(user_data),
            auth=('superadmin', 'superadmin')
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.text, 'email is required')

    def test_create_user_telephone_number(self):
        user_data = {
            'name': 'Jenya',
            'subname': 'Gusakovskaya',
            'age': 19,
            'country': 'Brest',
            'email': 'ololo.jeka@kek.com',
            'password': '345345'
        }

        resp = requests.post(
            os.path.join(ENDPOINT, 'api/users'),
            data=json.dumps(user_data),
            auth=('superadmin', 'superadmin')
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.text, 'telephone_number is required')

    def test_update_user(self):
        self.user_1['name'] = 'Kek'
        self.user_1['subname'] = 'Cheburek'

        resp = requests.put(
            os.path.join(ENDPOINT, 'api/users/{}'.format(self.user_1['id'])),
            data=json.dumps(dict(self.user_1.items())),
            auth=('superadmin', 'superadmin')
        )
        data = json.loads(resp.text)
        for key, value in self.user_1.items():
            self.assertEqual(data[key], value)

    def test_update_with_existed_email(self):
        self.user_1['name'] = 'Kek'
        self.user_1['subname'] = 'Cheburek'

        data = dict(self.user_1.items())
        data.update({'email': self.user_2['email']})

        resp = requests.put(
            os.path.join(ENDPOINT, 'api/users/{}'.format(self.user_1['id'])),
            data=json.dumps(data),
            auth=('superadmin', 'superadmin')
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.text, 'User with supplied email or telephone number already exists')

    def test_update_with_existed_telephone_number(self):
        self.user_1['name'] = 'Kek'
        self.user_1['subname'] = 'Cheburek'

        data = dict(self.user_1.items())
        data.update({'telephone_number': self.user_2['telephone_number']})

        resp = requests.put(
            os.path.join(ENDPOINT, 'api/users/{}'.format(self.user_1['id'])),
            data=json.dumps(data),
            auth=('superadmin', 'superadmin')
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.text, 'User with supplied email or telephone number already exists')


    def test_delete_user(self):
        resp = requests.delete(
            os.path.join(ENDPOINT, 'api/users/{}'.format(self.user_1['id'])),
            auth=('superadmin', 'superadmin')
        )
        self.assertEqual(resp.status_code, 204)

        resp = requests.get(
            os.path.join(ENDPOINT, 'api/users'),
            auth=('superadmin', 'superadmin')
        )
        data = json.loads(resp.text)
        self.assertEqual(len(data), len(self.list_db_user()))

    def test_user_avatar(self):
        # try to upload avatar
        resp = requests.put(
            os.path.join(ENDPOINT, 'api/users/{}/avatar'.format(self.user_1['id'])),
            auth=('superadmin', 'superadmin'),
            data=IMAGE_DATA_1
        )
        data = json.loads(resp.text)
        image_url = data['avatar']

        self.assertEqual(resp.status_code, 200)

        resp = requests.get(
            '{}{}'.format(ENDPOINT, image_url),
            auth=('superadmin', 'superadmin')
        )

        self.assertEqual(IMAGE_DATA_1, resp.content)

        # not send imghash param
        resp = requests.get(
            os.path.join(ENDPOINT, 'api/users/{}/avatar'.format(self.user_1['id'])),
            auth=('superadmin', 'superadmin')
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.text, 'imghash is required')

        # send invalid imghash
        resp = requests.get(
            os.path.join(ENDPOINT, 'api/users/{}/avatar?imghash=123'.format(self.user_1['id'])),
            auth=('superadmin', 'superadmin')
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.text, 'Invalid imghash')

        resp = requests.get(
            os.path.join(ENDPOINT, 'api/users/{}'.format(self.user_1['id'])),
            auth=('superadmin', 'superadmin')
        )
        current_user_state = json.loads(resp.text)

        self.assertEqual(resp.status_code, 200)

        # try to upload another avatar
        resp = requests.put(
            os.path.join(ENDPOINT, 'api/users/{}/avatar'.format(self.user_1['id'])),
            auth=('superadmin', 'superadmin'),
            data=IMAGE_DATA_2
        )

        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.text)
        image_url_updated = data['avatar']

        resp = requests.get(
            '{}{}'.format(ENDPOINT, image_url_updated),
            auth=('superadmin', 'superadmin')
        )

        self.assertEqual(IMAGE_DATA_2, resp.content)

        # check deletion of old avatar
        with self.assertRaises(ClientError):
            client.head_object(
                Bucket='users',
                Key='{}/{}'.format(
                    current_user_state['id'],
                    current_user_state['avatar_token']
                )
            )


if __name__ == '__main__':
    wait_web()
    unittest.main()