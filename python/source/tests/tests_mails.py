import os
import unittest
import requests
import json
import logging

from tests_mixins import DbMixin
from tests_settings import ENDPOINT
from tests_settings import IMAGE_DATA_1


class MailsTests(unittest.TestCase, DbMixin):

    def setUp(self):
        self.erase_db('mail_user')
        self.erase_db('mail_mail')

        self.superadmin = self.add_db_object(
            'mail_user',
            {
                'email': 'superadmin',
                'password': 'superadmin'
            }
        )

        self.user_1 = self.add_db_object(
            'mail_user',
            {
                'name': 'Alexey',
                'subname': 'Safronov',
                'age': 20,
                'country': 'Mogilev',
                'telephone_number': '222322',
                'email': 'diamond.alex97@gmail.com',
                'password': '123',
                'avatar_url': '',
                'avatar_token': ''
            }
        )

        self.user_2 = self.add_db_object(
            'mail_user',
            {
                'name': 'Vlad',
                'subname': 'Punko',
                'age': 20,
                'country': 'Brest',
                'telephone_number': '345345345',
                'email': 'punko.kek@vlad.com',
                'password': '2345',
                'avatar_url': '',
                'avatar_token': ''
            }
        )

        self.mail_1 = self.add_db_object(
            'mail_mail',
            {
                'header': 'Mail1',
                'content': 'Hello',
                'sender_id': self.user_1['id'],
                'recipient_id': self.user_2['id'],
                'is_deleted': False
            }
        )

        self.mail_2 = self.add_db_object(
            'mail_mail',
            {
                'header': 'Mail2',
                'content': 'Hello',
                'sender_id': self.user_1['id'],
                'recipient_id': self.user_2['id'],
                'is_deleted': False
            }
        )

    def test_list_mails(self):
        resp = requests.get(
            os.path.join(ENDPOINT, 'api/mails'),
            auth=('superadmin', 'superadmin')
        )
        data = json.loads(resp.text)

        for response, mail in zip(data, [self.mail_1, self.mail_2]):
            for key, value in mail.items():
                self.assertEqual(response[key], value)

    def test_get_mail(self):
        resp = requests.get(
            os.path.join(ENDPOINT, 'api/mails/{}'.format(self.mail_1['id'])),
            auth=('superadmin', 'superadmin')
        )

        self.assertEqual(resp.status_code, 200)

        data = json.loads(resp.text)
        for key, value in self.mail_1.items():
            self.assertEqual(data[key], value)

    def test_create_mail(self):
        mail_data = {
            'header': 'NewMail',
            'content': 'Kek',
            'sender_id': self.user_2['id'],
            'recipient_id': self.user_1['id'],
            'is_deleted': False
        }

        resp = requests.post(
            os.path.join(ENDPOINT, 'api/mails'),
            data=json.dumps(mail_data),
            auth=('superadmin', 'superadmin')
        )

        self.assertEqual(resp.status_code, 201)

        data = json.loads(resp.text)
        for key, value in mail_data.items():
            self.assertEqual(data[key], value)

        resp = requests.get(
            os.path.join(ENDPOINT, 'api/mails'),
            auth=('superadmin', 'superadmin')
        )

        data = json.loads(resp.text)
        self.assertEqual(len(data), len(self.list_db_objects('mail_mail')))

    def test_create_mail_with_not_existed_sender(self):
        mail_data = {
            'header': 'NewMail',
            'content': 'Kek',
            'sender_id': 0,
            'is_deleted': False
        }

        resp = requests.post(
            os.path.join(ENDPOINT, 'api/mails'),
            data=json.dumps(mail_data),
            auth=('superadmin', 'superadmin')
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.text, 'User with supplied id: 0 does not exists')

    def test_create_mail_with_not_recipient_sender(self):
        mail_data = {
            'header': 'NewMail',
            'content': 'Kek',
            'sender_id': self.user_1['id'],
            'recipient_id': 0,
            'is_deleted': False
        }

        resp = requests.post(
            os.path.join(ENDPOINT, 'api/mails'),
            data=json.dumps(mail_data),
            auth=('superadmin', 'superadmin')
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.text, 'User with supplied id: 0 does not exists')

    def test_update_mail(self):
        self.mail_1['content'] = 'Updated content'
        resp = requests.put(
            os.path.join(ENDPOINT, 'api/mails/{}'.format(self.mail_1['id'])),
            data=json.dumps(dict(self.mail_1.items())),
            auth=('superadmin', 'superadmin')
        )
        data = json.loads(resp.text)
        for key, value in self.mail_1.items():
            self.assertEqual(data[key], value)

    def test_update_mail_with_not_existed_sender(self):
        self.mail_1['sender_id'] = 0
        resp = requests.put(
            os.path.join(ENDPOINT, 'api/mails/{}'.format(self.mail_1['id'])),
            data=json.dumps(dict(self.mail_1.items())),
            auth=('superadmin', 'superadmin')
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.text, 'User with supplied id: 0 does not exists')

    def test_update_mail_with_not_existed_recipient(self):
        self.mail_1['recipient_id'] = 0
        resp = requests.put(
            os.path.join(ENDPOINT, 'api/mails/{}'.format(self.mail_1['id'])),
            data=json.dumps(dict(self.mail_1.items())),
            auth=('superadmin', 'superadmin')
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.text, 'User with supplied id: 0 does not exists')

    def test_delete_mail(self):
        resp = requests.delete(
            os.path.join(ENDPOINT, 'api/mails/{}'.format(self.mail_1['id'])),
            auth=('superadmin', 'superadmin')
        )
        self.assertEqual(resp.status_code, 204)

        resp = requests.get(
            os.path.join(ENDPOINT, 'api/mails'),
            auth=('superadmin', 'superadmin')
        )
        data = json.loads(resp.text)
        self.assertEqual(len(data), len(self.list_db_objects('mail_mail')))

    def test_mail_data(self):
        # try to put file to not existed mail
        resp = requests.post(
            os.path.join(ENDPOINT, 'api/mails/0/files'),
            auth=('superadmin', 'superadmin')
        )
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.text, 'Not found')

        # try to put file to existed mail
        resp = requests.post(
            os.path.join(ENDPOINT, 'api/mails/{}/files'.format(self.mail_1['id'])),
            data=IMAGE_DATA_1,
            auth=('superadmin', 'superadmin')
        )

        data = json.loads(resp.text)
        self.assertEqual(resp.status_code, 200)


        # try to get uploaded file info
        resp = requests.get(
            os.path.join(ENDPOINT, 'api/mails/{}/files/{}'.format(self.mail_1['id'],
                                                                  data['id'])),
            auth=('superadmin', 'superadmin')
        )
        data_info = json.loads(resp.text)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data_info['data_url'], data['data_url'])


        # try to get uploaded file content
        resp = requests.get(
            '{}{}'.format(ENDPOINT, data['data_url']),
            auth=('superadmin', 'superadmin')
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, IMAGE_DATA_1)


if __name__ == '__main__':
    unittest.main()