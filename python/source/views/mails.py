import random

import db
import exceptions
import psycopg2.extras
import json

from views.base import BaseViewSet
from aiohttp import web
from storage import client
from botocore.client import ClientError
from aiohttp_session import get_session


class MailViewSet(BaseViewSet):

    FIELDS = ('id',
              'header',
              'content',
              'sender_id',
              'recipient_id',
              'mailgroup_id')

    PK = 'id'
    DB_TABLE = 'maildrive_mail'

    def __init__(self, dbpool):
        self._dbpool = dbpool

    def register_routes(self, router):
        router.add_get('/api/mails', self.list_mails)
        router.add_get('/api/mails/{id:\d+}', self.retrieve_mail)
        router.add_post('/api/mails', self.create_mail)
        router.add_put('/api/mails/{id:\d+}', self.update_object)
        router.add_delete('/api/mails/{id:\d+}', self.delete_mail)

        router.add_get('/api/mails/{mail_id:\d+}/files', self.list_mail_files)
        router.add_get('/api/mails/{mail_id:\d+}/files/{file_id:\d+}', self.get_mail_file)
        router.add_get('/api/mails/{mail_id:\d+}/files/{file_id:\d+}/data', self.get_mail_file_data)

        router.add_post('/api/mails/{mail_id:\d+}/files', self.add_mail_file)
        router.add_delete('/api/mails/{mail_id:\d+}/files/{file_id:\d+}', self.delete_mail_file)

        router.add_post('/api/mails/{mail_id:\d+}/send', self.send)

    async def validate_sender_id(self, request_data):
        if 'sender_id' not in request_data:
            raise exceptions.FieldRequired('sender_id')

        sender_id = request_data.get('sender_id')
        async with self._dbpool.acquire() as conn:
            data = await db.exec_universal_select_query(
                'maildrive_user',
                where={
                    'email': sender_id,
                },
                one=True,
                conn=conn
            )
            if not data:
                raise exceptions.UserDoesNotExists(sender_id)

    async def validate_recipient_id(self, request_data):
        recipient_id = request_data.get('recipient_id')
        if recipient_id is not None:
            async with self._dbpool.acquire() as conn:
                data = await db.exec_universal_select_query(
                    'maildrive_user',
                    where={
                        'email': recipient_id,
                    },
                    one=True,
                    conn=conn
                )
                if not data:
                    raise exceptions.UserDoesNotExists(recipient_id)

    async def list_mails(self, request):
        response = await self.list_objects(request)
        if response.status != 200:
            return response

        session = await get_session(request)
        user_id = session['email']

        mails = json.loads(response.body.decode())
        for mail in mails:
            mail['mailgroup_id'] = await self.get_mailgroup_id(user_id, mail['id'])
        return web.json_response(mails)

    async def retrieve_mail(self, request):
        response = await self.retrieve_object(request)
        if response.status != 200:
            return response

        session = await get_session(request)
        user_id = session['email']

        mail = json.loads(response.body.decode())
        mail['mailgroup_id'] = await self.get_mailgroup_id(user_id, mail['id'])
        return web.json_response(mail)

    async def create_mail(self, request):
        request_data = await request.json()

        try:
            await self.validation_request_data(request_data, 'post')
        except exceptions.MailDrive as e:
            return web.Response(text=str(e), status=400)

        async with self._dbpool.acquire() as conn:
            data = await db.exec_universal_insert_query(
                self.DB_TABLE,
                set=request_data,
                conn=conn
            )
            await db.exec_universal_insert_query(
                'maildrive_user_mail',
                set={
                    'user_id': request_data['sender_id'],
                    'mail_id': data['id'],
                    'mailgroup_id': 3
                },
                conn=conn
            )
        return web.json_response(dict(data), status=201)

    async def send(self, request):
        mail_id = int(request.match_info['mail_id'])
        mail = await self.get_object(self.DB_TABLE,
                                     where={'id': mail_id})
        if not mail:
            return web.Response(text='Not found', status=404)

        if 'recipient_id' not in mail:
            exceptions.MailRecipientNotExist()

        async with self._dbpool.acquire() as conn:
            sender_user_mail = await db.exec_universal_select_query(
                'maildrive_user_mail',
                where={
                    'user_id': mail['sender_id'],
                    'mail_id': mail['id']
                },
                one=True,
                conn=conn
            )

            if sender_user_mail['mailgroup_id'] == 2:
                return web.Response(text='Mail already sended', status=400)

            await db.exec_universal_update_query(
                'maildrive_user_mail',
                set={
                    'mailgroup_id': 2
                },
                where={
                    'id': sender_user_mail['id']
                },
                conn=conn
            )
            await db.exec_universal_insert_query(
                'maildrive_user_mail',
                set={
                    'user_id': mail['recipient_id'],
                    'mail_id': mail['id'],
                    'mailgroup_id': 1
                },
                conn=conn
            )
        return web.Response(text='Mail sended', status=200)

    async def list_mail_files(self, request):
        mail_id = int(request.match_info['mail_id'])
        mail = await self.get_object(self.DB_TABLE,
                                     where={'id': mail_id})
        if not mail:
            return web.Response(text='Not found', status=404)

        async with self._dbpool.acquire() as conn:
            data = await db.exec_universal_select_query(
                'maildrive_mail_data',
                where={
                    'mail_id': mail['id']
                },
                conn=conn
            )
            data = list(map(dict, data))
            return web.json_response(data, status=200)

    async def get_mail_file(self, request):
        mail_id = int(request.match_info['mail_id'])
        mail = await self.get_object(self.DB_TABLE,
                                     where={'id': mail_id})
        if not mail:
            return web.Response(text='Not found', status=404)

        file_id = int(request.match_info['file_id'])
        async with self._dbpool.acquire() as conn:
            file = await db.exec_universal_select_query(
                'maildrive_mail_data',
                where={
                    'id': file_id,
                    'mail_id': mail_id
                },
                one=True,
                conn=conn
            )

        if not file:
            return web.Response(text='Not found', status=404)
        return web.json_response(dict(file), status=200)

    async def get_mail_file_data(self, request):
        mail_id = int(request.match_info['mail_id'])
        mail = await self.get_object(self.DB_TABLE,
                                     where={'id': mail_id})
        if not mail:
            return web.Response(text='Not found', status=404)

        file_id = int(request.match_info['file_id'])
        async with self._dbpool.acquire() as conn:
            file = await db.exec_universal_select_query(
                'maildrive_mail_data',
                where={
                    'id': file_id,
                    'mail_id': mail_id
                },
                one=True,
                conn=conn
            )

        if not file:
            return web.Response(text='Not found', status=404)

        if 'datahash' not in request.query:
            return web.Response(text='datahash is required', status=400)

        if file['data_token'] != request.query['datahash']:
            return web.Response(text='Invalid datahash', status=400)

        data_key = '{}/files/{}/{}'.format(mail_id, file['id'], file['data_token'])
        try:
            client.head_object(
                Bucket='mails',
                Key=data_key,
            )
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return web.Response(text='Data not set', status=404)

        s3_object = client.get_object(
            Bucket='mails',
            Key=data_key
        )

        content = s3_object['Body'].read()
        return web.Response(body=content, status=200, content_type=s3_object['ContentType'])

    async def add_mail_file(self, request):
        mail_id = int(request.match_info['mail_id'])
        mail = await self.get_object(self.DB_TABLE,
                                     where={'id': mail_id})
        if not mail:
            return web.Response(text='Not found', status=404)

        data = await request.post()
        if 'file' not in data:
            return web.Response(text='file form field not set', status=400)

        async with self._dbpool.acquire() as conn:
            db_file = await db.exec_universal_insert_query(
                'maildrive_mail_data',
                set={
                    'mail_id': mail_id
                },
                conn=conn
            )

            token = random.getrandbits(64)
            data_url = '/api/mails/{}/files/{}/data?datahash={}'.format(mail_id, db_file['id'], token)

            updated_db_file = await db.exec_universal_update_query(
                'maildrive_mail_data',
                set={
                    'data_url': data_url,
                    'data_token': token
                },
                where={
                    'id': db_file['id']
                },
                conn=conn
            )

        content = data['file'].file.read()
        client.put_object(Bucket='mails',
                          Key='{}/files/{}/{}'.format(mail_id, db_file['id'], token),
                          Body=content)

        return web.json_response(dict(updated_db_file), status=200)

    async def delete_mail_file(self, request):
        mail_id = int(request.match_info['mail_id'])
        mail = await self.get_object(self.DB_TABLE,
                                     where={'id': mail_id})
        if not mail:
            return web.Response(text='Not found', status=404)

        file_id = int(request.match_info['file_id'])
        async with self._dbpool.acquire() as conn:
            file = await db.exec_universal_select_query(
                'maildrive_mail_data',
                where={
                    'id': file_id,
                    'mail_id': mail_id
                },
                conn=conn
            )

        if not file:
            return web.Response(text='Not found', status=404)


        async with self._dbpool.acquire() as conn:
            await db.exec_universal_delete_query(
                'maildrive_mail_data',
                where={
                    'id': file_id,
                },
                conn=conn
            )

        client.delete_object(
            Bucket='mails',
            Key='{}/files/{}/{}'.format(mail_id, file['id'], file['data_token']),
        )
        return web.Response(status=204)

    async def delete_mail(self, request):

        object_id = int(request.match_info[self.PK])

        object = await self.get_object(self.DB_TABLE,
                                       where={self.PK: object_id})
        if not object:
            return web.Response(text='Not found', status=404)

        async with self._dbpool.acquire() as conn:
            await db.exec_universal_delete_query(
                'maildrive_mail_data',
                where={
                    'mail_id': object_id,
                },
                conn=conn
            )
            await db.exec_universal_delete_query(
                'maildrive_user_mail',
                where={
                    'mail_id': object_id,
                },
                conn=conn
            )
            await db.exec_universal_delete_query(
                self.DB_TABLE,
                where={self.PK: object_id},
                conn=conn
            )

        return web.json_response(status=204)
