import random

import db
import exceptions
import psycopg2.extras

from views.base import BaseViewSet
from aiohttp import web
from storage import client
from botocore.client import ClientError


class MailViewSet(BaseViewSet):

    FIELDS = ('id',
              'header',
              'content',
              'sender_id',
              'recipient_id')

    OBJECT_ID = 'mail_id'
    DB_TABLE = 'maildrive_mail'

    def __init__(self, dbpool):
        self._dbpool = dbpool

    def register_routes(self, router):
        router.add_get('/api/mails', self.list_objects)
        router.add_get('/api/mails/{mail_id:\d+}', self.retrieve_object)
        router.add_post('/api/mails', self.create_object)
        router.add_put('/api/mails/{mail_id:\d+}', self.update_object)
        router.add_delete('/api/mails/{mail_id:\d+}', self.delete_object)

        router.add_get('/api/mails/{mail_id:\d+}/files', self.list_mail_files)
        router.add_get('/api/mails/{mail_id:\d+}/files/{file_id:\d+}', self.get_mail_file)
        router.add_get('/api/mails/{mail_id:\d+}/files/{file_id:\d+}/data', self.get_mail_file_data)

        router.add_post('/api/mails/{mail_id:\d+}/files', self.add_mail_file)
        router.add_delete('/api/mails/{mail_id:\d+}/files/{file_id:\d+}', self.delete_mail_file)

    async def validate_sender_id(self, request_data):
        if 'sender_id' not in request_data:
            raise exceptions.FieldRequired('sender_id')

        sender_id = request_data.get('sender_id')
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    db.build_universal_select_query(
                        'maildrive_user',
                        where={
                            'id': sender_id,
                        }
                    )
                )
                data = await cursor.fetchone()
                if not data:
                    raise exceptions.UserDoesNotExists(sender_id)

    async def validate_recipient_id(self, request_data):
        recipient_id = request_data.get('recipient_id')
        if recipient_id is not None:
            async with self._dbpool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        db.build_universal_select_query(
                            'maildrive_user',
                            where={
                                'id': recipient_id,
                            }
                        )
                    )
                    data = await cursor.fetchone()
                    if not data:
                        raise exceptions.UserDoesNotExists(recipient_id)

    async def list_mail_files(self, request):
        mail_id = int(request.match_info['mail_id'])
        mail = await self.get_object(self.DB_TABLE,
                                     where={'id': mail_id})
        if not mail:
            return web.Response(text='Not found', status=404)

        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    'SELECT * FROM {} \
                        INNER JOIN \
                            maildrive_mail ON maildrive_mail.id = maildrive_mail_data.mail_id;'.format('maildrive_mail_data')
                )
                data = await self._fetch_all(cursor)
                return web.json_response(data, status=200)

    async def get_mail_file(self, request):
        mail_id = int(request.match_info['mail_id'])
        mail = await self.get_object(self.DB_TABLE,
                                     where={'id': mail_id})
        if not mail:
            return web.Response(text='Not found', status=404)

        file_id = int(request.match_info['file_id'])
        async with self._dbpool.acquire() as conn:
            async with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                await cursor.execute(
                    db.build_universal_select_query(
                        'maildrive_mail_data',
                        where={
                            'id': file_id,
                            'mail_id': mail_id
                        }
                    )
                )
                file = await cursor.fetchone()

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
            async with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                await cursor.execute(
                    db.build_universal_select_query(
                        'maildrive_mail_data',
                        where={
                            'id': file_id,
                            'mail_id': mail_id
                        }
                    )
                )
                file = await cursor.fetchone()

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
        return web.Response(body=content, status=200)

    async def add_mail_file(self, request):
        mail_id = int(request.match_info['mail_id'])
        mail = await self.get_object(self.DB_TABLE,
                                     where={'id': mail_id})
        if not mail:
            return web.Response(text='Not found', status=404)

        async with self._dbpool.acquire() as conn:
            async with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                await cursor.execute(
                    db.build_universal_insert_query(
                        'maildrive_mail_data',
                        set={
                            'mail_id': mail_id
                        }
                    )
                )
                db_file = await cursor.fetchone()

                token = random.getrandbits(64)
                data_url = '/api/mails/{}/files/{}/data?datahash={}'.format(mail_id, db_file['id'], token)

                await cursor.execute(
                    db.build_universal_update_query(
                        'maildrive_mail_data',
                        set={
                            'data_url': data_url,
                            'data_token': token
                        },
                        where={
                            'id': db_file['id']
                        }
                    )
                )
                updated_db_file = await cursor.fetchone()

        content = await self.read_content(request)
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
            async with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                await cursor.execute(
                    db.build_universal_select_query(
                        'maildrive_mail_data',
                        where={
                            'id': file_id,
                            'mail_id': mail_id
                        }
                    )
                )
                file = await cursor.fetchone()

        if not file:
            return web.Response(text='Not found', status=404)

        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    db.build_universal_delete_query(
                        'maildrive_mail_data',
                        where={
                            'id': file_id,
                        }
                    )
                )

        client.delete_object(
            Bucket='mails',
            Key='{}/files/{}/{}'.format(mail_id, file['id'], file['data_token']),
        )
        return web.Response(status=204)



