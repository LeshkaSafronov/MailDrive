import os
import unittest
import settings
import psycopg2
import psycopg2.extras
import logging
import db
import json

import requests
import time


WEB_HOST = os.environ['WEB_HOST']
WEB_PORT = os.environ['WEB_PORT']

ENDPOINT = 'http://{}:{}/api'.format(WEB_HOST, WEB_PORT)


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
                'password': '123'
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
                'password': '2345'
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
                'password': '657'
            }
        )

    def test_basic_auth(self):
        resp_without_auth = requests.get(ENDPOINT)
        self.assertEqual(resp_without_auth.status_code, 401)

        resp = requests.get(ENDPOINT, auth=('superadmin', 'superadmin'))
        self.assertEqual(resp.status_code, 200)

    def test_auth_via_session(self):
        with requests.session() as session:
            resp = session.get(ENDPOINT)
            self.assertEqual(resp.status_code, 401)

            resp = session.post(
                os.path.join(ENDPOINT, 'users/login'),
                data=json.dumps(
                    {
                        'email': 'diamond.alex97@gmail.com',
                        'password': '123'
                    }
                )
            )
            self.assertEqual(resp.status_code, 200)

            resp = session.get(ENDPOINT)
            self.assertEqual(resp.status_code, 200)

    def test_wrong_basic_auth(self):
        resp = requests.get(ENDPOINT, auth=('superadmin', 'kek'))
        self.assertEqual(resp.status_code, 401)

    def test_wrong_json_auth(self):
        resp = requests.post(
            os.path.join(ENDPOINT, 'users/login'),
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
                os.path.join(ENDPOINT, 'users/0'),
                auth=('superadmin', 'superadmin')
            )
            self.assertEqual(resp.status_code, 404)
            self.assertEqual(resp.text, 'User not found')

    def test_list_users(self):
        resp = requests.get(
            os.path.join(ENDPOINT, 'users'),
            auth=('superadmin', 'superadmin')
        )
        data = json.loads(resp.text)

        for response, user in zip(data, [self.superadmin, self.user_1, self.user_2, self.user_3]):
            for key, value in user.items():
                self.assertEqual(response[key], value)

    def test_get_user(self):
        resp = requests.get(
            os.path.join(ENDPOINT, 'users/{}'.format(self.user_2['id'])),
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
            os.path.join(ENDPOINT, 'users'),
            data=json.dumps(user_data),
            auth=('superadmin', 'superadmin')
        )

        self.assertEqual(resp.status_code, 201)

        data = json.loads(resp.text)
        for key, value in user_data.items():
            self.assertEqual(data[key], value)

        resp = requests.get(
            os.path.join(ENDPOINT, 'users'),
            auth=('superadmin', 'superadmin')
        )

        data = json.loads(resp.text)
        self.assertEqual(len(data), len(self.list_db_user()))

    def test_update_user(self):
        self.user_1['name'] = 'Kek'
        self.user_1['subname'] = 'Cheburek'

        resp = requests.put(
            os.path.join(ENDPOINT, 'users/{}'.format(self.user_1['id'])),
            data=json.dumps(dict(self.user_1.items())),
            auth=('superadmin', 'superadmin')
        )

        data = json.loads(resp.text)
        for key, value in self.user_1.items():
            self.assertEqual(data[key], value)

    def test_delete_user(self):
        resp = requests.delete(
            os.path.join(ENDPOINT, 'users/{}'.format(self.user_1['id'])),
            auth=('superadmin', 'superadmin')
        )
        self.assertEqual(resp.status_code, 204)

        resp = requests.get(
            os.path.join(ENDPOINT, 'users'),
            auth=('superadmin', 'superadmin')
        )
        data = json.loads(resp.text)
        self.assertEqual(len(data), len(self.list_db_user()))


if __name__ == '__main__':
    wait_web()
    unittest.main()