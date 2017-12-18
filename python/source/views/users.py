import random
import exceptions
import db
import psycopg2
import psycopg2.extras
import json

from aiohttp import web
from aiohttp_session import get_session
from views.base import BaseViewSet
from storage import client
from botocore.exceptions import ClientError


class UserViewSet(BaseViewSet):

    FIELDS = ('name',
              'subname',
              'age',
              'country',
              'telephone_number',
              'email',
              'password',
              'avatar_url',
              'avatar_token')

    PK = 'email'
    DB_TABLE = 'maildrive_user'

    def __init__(self, dbpool):
        self._dbpool = dbpool

    def register_routes(self, router):
        router.add_get('/api/users/is_auth', self.get_auth_user)
        router.add_get('/api/users', self.list_objects)
        router.add_get('/api/users/{email}', self.retrieve_object)
        router.add_post('/api/users', self.create_object)
        router.add_put('/api/users/{email}', self.update_object)
        router.add_delete('/api/users/{email}', self.delete_object)

        router.add_post('/api/users/login', self.login)
        router.add_post('/api/users/logout', self.logout)

        router.add_get('/api/users/{email}/avatar', self.get_avatar)
        router.add_put('/api/users/{email}/avatar', self.set_avatar)
        router.add_post('/api/users/singup', self.create_object)
        router.add_get('/api/users/{email}/mails', self.get_mails)

    async def get_auth_user(self, request):
        session = await get_session(request)
        request.match_info[self.PK] = session[self.PK]
        return await self.retrieve_object(request)

    async def validate_email(self, request_data):
        if 'email' not in request_data:
            raise exceptions.FieldRequired('email')

        email = request_data.get('email')
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    db.build_universal_select_query(
                        'maildrive_user',
                        where={
                            'email': email,
                        }
                    )
                )
                data = await cursor.fetchone()
                if data:
                    raise exceptions.UserExists()

    async def validate_telephone_number(self, request_data):
        if 'telephone_number' not in request_data:
            raise exceptions.FieldRequired('telephone_number')

        telephone_number = request_data.get('telephone_number')
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    db.build_universal_select_query(
                        'maildrive_user',
                        where={
                            'telephone_number': telephone_number,
                        }
                    )
                )
                data = await cursor.fetchone()
                if data:
                    raise exceptions.UserExists()

    async def login(self, request):
        request_json = await request.json()
        email, password = request_json['email'], request_json['password']

        async with self._dbpool.acquire() as conn:
            async with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                await cursor.execute(
                    db.build_universal_select_query(
                        'maildrive_user',
                        where={
                            'email': email,
                            'password': password
                        }
                    )
                )
                data = await cursor.fetchone()
                if data:
                    session = await get_session(request)
                    session['authorized'] = True
                    session[self.PK] = data[self.PK]
                    return web.Response(status=200)
                else:
                    return web.Response(text='Invalide email or password', status=400)

    async def logout(self, request):
        session = await get_session(request)
        session.pop('authorized', None)
        return web.Response(status=200)

    async def get_avatar(self, request):
        user_id = int(request.match_info[self.PK])
        user = await self.get_object('maildrive_user',
                                     where={self.PK: user_id})
        if not user:
            return web.Response(text='Not found', status=404)

        if 'imghash' not in request.query:
            return web.Response(text='imghash is required', status=400)

        if user['avatar_token'] != request.query['imghash']:
            return web.Response(text='Invalid imghash', status=400)

        object_key = '{}/{}'.format(user_id, user['avatar_token'])

        try:
            client.head_object(
                Bucket='users',
                Key=object_key
            )
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return web.Response(text='Image is not set', status=404)

        file = client.get_object(
            Bucket='users',
            Key=object_key
        )

        content = file['Body'].read()
        return web.Response(body=content, status=200, content_type=file['ContentType'])

    async def set_avatar(self, request):
        user_id = int(request.match_info[self.PK])

        user = await self.get_object('maildrive_user',
                                     where={self.PK: user_id})
        if not user:
            return web.Response(text='Not found', status=404)

        data = await request.post()
        if 'image' not in data:
            return web.Response(text='image form field not set', status=400)

        client.delete_object(
            Bucket='users',
            Key='{}/{}'.format(user_id, user['avatar_token'])
        )

        token = random.getrandbits(64)
        avatar_url = '/api/users/{}/avatar?imghash={}'.format(user_id, token)

        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    db.build_universal_update_query(
                        'maildrive_user',
                        set={
                            'avatar_url': avatar_url,
                            'avatar_token': token
                        },
                        where={self.PK: user_id}
                    )
                )

        content = data['image'].file.read()
        client.put_object(Bucket='users',
                          Key='{}/{}'.format(user_id, token),
                          Body=content)
        return web.json_response({'avatar_url': avatar_url}, status=200)

    async def get_mails(self, request):
        response_user = await self.retrieve_object(request)
        if response_user.status == 404:
            return response_user

        user = json.loads(response_user.body.decode())

        where = {
            'user_id': user[self.PK]
        }

        mailgroup_id = request.query.get('mailgroup_id')
        if mailgroup_id:
            where.update({'mailgroup_id': int(mailgroup_id)})

        async with self._dbpool.acquire() as conn:
            async with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                await cursor.execute(
                    db.build_universal_select_query(
                        'maildrive_user_mail',
                        where=where
                    )
                )
                records = await cursor.fetchall()
                mails = []
                if records:
                    mail_ids = tuple(record['mail_id'] for record in records)
                    await cursor.execute(
                        "SELECT * FROM maildrive_mail WHERE id IN {}".format(mail_ids)
                    )
                    mails = list(map(dict, await cursor.fetchall()))
                    for mail in mails:
                        mail['mailgroup_id'] = await self.get_mailgroup_id(user['email'], mail['id'])
        return web.json_response(mails)