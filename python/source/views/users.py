import random
import exceptions
import db
import logging

from aiohttp import web
from aiohttp_session import get_session
from views.base import BaseViewSet
from storage import client
from botocore.exceptions import ClientError


class UserViewSet(BaseViewSet):

    FIELDS = ('id',
              'name',
              'subname',
              'age',
              'country',
              'telephone_number',
              'email',
              'password',
              'avatar_url',
              'avatar_token')

    OBJECT_ID = 'user_id'
    DB_TABLE = 'maildrive_user'

    def __init__(self, dbpool):
        self._dbpool = dbpool

    def register_routes(self, router):
        router.add_get('/api/users', self.list_objects)
        router.add_get('/api/users/{user_id:\d+}', self.retrieve_object)
        router.add_post('/api/users', self.create_object)
        router.add_put('/api/users/{user_id:\d+}', self.update_object)
        router.add_delete('/api/users/{user_id:\d+}', self.delete_object)

        router.add_post('/api/users/login', self.login)
        router.add_post('/api/users/logout', self.logout)

        router.add_get('/api/users/{user_id:\d+}/avatar', self.get_avatar)
        router.add_put('/api/users/{user_id:\d+}/avatar', self.set_avatar)
        router.add_post('/api/users/singup', self.create_object)
        router.add_get('/api/users/is_auth', self.get_auth_user)

    async def get_auth_user(self, request):
        session = await get_session(request)
        request.match_info[self.OBJECT_ID] = session['user_id']
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
            async with conn.cursor() as cursor:
                await cursor.execute(
                    db.build_universal_select_query(
                        'maildrive_user',
                        where={
                            'email': email,
                            'password': password
                        }
                    )
                )
                data = await self._fetch_one(cursor)
                if data:
                    session = await get_session(request)
                    session['authorized'] = True
                    session['user_id'] = data['id']
                    return web.Response(status=200)
                else:
                    return web.Response(text='Invalide email or password', status=400)

    async def logout(self, request):
        session = await get_session(request)
        session.pop('authorized', None)
        return web.Response(status=200)

    async def get_avatar(self, request):
        user_id = int(request.match_info['user_id'])
        user = await self.get_object('maildrive_user',
                                     where={'id': user_id})
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
        user_id = int(request.match_info['user_id'])

        user = await self.get_object('maildrive_user',
                                     where={'id': user_id})
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
                        where={'id': user_id}
                    )
                )

        image = data['image']
        file = image.file
        content = file.read()

        client.put_object(Bucket='users',
                          Key='{}/{}'.format(user_id, token),
                          Body=content)
        return web.json_response({'avatar_url': avatar_url}, status=200)