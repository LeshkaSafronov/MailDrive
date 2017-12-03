import os
import unittest
import requests
import json
import logging

from tests_mixins import DbMixin
from tests_settings import ENDPOINT


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
                'avatar': '',
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
                'avatar': '',
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




if __name__ == '__main__':
    unittest.main()