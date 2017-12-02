import random

import db

from aiohttp import web
from aiohttp_session import get_session
from mixins.base import BaseMixinView
from storage import client
from botocore.exceptions import ClientError


class UserMixinView(BaseMixinView):

    FIELDS = ('id',
              'name',
              'subname',
              'age',
              'country',
              'telephone_number',
              'email',
              'password',
              'avatar',
              'avatar_token')

    def _register_routes(self):
        self.router.add_get('/api/users', self.list_users)
        self.router.add_get('/api/users/{user_id:\d+}', self.retrieve_user)
        self.router.add_post('/api/users', self.create_user)
        self.router.add_put('/api/users/{user_id:\d+}', self.update_user)
        self.router.add_delete('/api/users/{user_id:\d+}', self.delete_user)

        self.router.add_post('/api/users/login', self.login)
        self.router.add_post('/api/users/logout', self.logout)

        self.router.add_get('/api/users/{user_id:\d+}/avatar', self.get_avatar)
        self.router.add_put('/api/users/{user_id:\d+}/avatar', self.set_avatar)


    async def list_users(self, request):
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(db.build_universal_select_query('mail_user'))
                data = await self._fetch_all(cursor)
        return web.json_response(data=data)

    async def retrieve_user(self, request):
        user_id = int(request.match_info['user_id'])
        user = await self.get_object('mail_user',
                                     where={'id': user_id})
        if not user:
            return web.Response(text='User not found', status=404)
        else:
            return web.json_response(user)

    async def create_user(self, request):
        request_json = await request.json()
        email, telephone_number = request_json['email'], request_json['telephone_number']

        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:

                await cursor.execute(db.build_universal_select_query(
                    'mail_user',
                    where={
                        'email': email,
                        'telephone_number': telephone_number
                    },
                    sep=' OR ')
                )
                founded_users = await self._fetch_all(cursor)
                if founded_users:
                    return web.Response(text='User with supplied email or telephone number already exists',
                                        status=400)

                await cursor.execute(db.build_universal_insert_query('mail_user',
                                                                     fields=request_json.keys(),
                                                                     values=request_json.values()))

                data = await self._fetch_one(cursor)
        return web.json_response(data, status=201)

    async def update_user(self, request):
        user_id = int(request.match_info['user_id'])

        user = await self.get_object('mail_user',
                                     where={'id': user_id})
        if not user:
            return web.Response(text='User not found', status=404)

        request_json = await request.json()
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(db.build_universal_update_query('mail_user',
                                                                     set=request_json,
                                                                     where={'id': user_id}))
                data = await self._fetch_one(cursor)
        return web.json_response(data, status=200)

    async def delete_user(self, request):
        user_id = int(request.match_info['user_id'])

        user = await self.get_object('mail_user',
                                     where={'id': user_id})
        if not user:
            return web.Response(text='User not found', status=404)

        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(db.build_universal_delete_query('mail_user',
                                                                     where={'id': user_id}))
        return web.json_response(status=204)

    async def login(self, request):
        request_json = await request.json()
        email, password = request_json['email'], request_json['password']

        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    db.build_universal_select_query(
                        'mail_user',
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
                    return web.Response(status=200)
                else:
                    return web.Response(text='Invalide email or password', status=400)

    async def logout(self, request):
        session = await get_session(request)
        session.pop('authorized', None)
        return web.Response(status=200)

    async def get_avatar(self, request):
        user_id = int(request.match_info['user_id'])
        user = await self.get_object('mail_user',
                                     where={'id': user_id})
        if not user:
            return web.Response(text='User not found', status=404)

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
        return web.Response(body=content, status=200, content_type='image/jpeg')

    async def set_avatar(self, request):
        user_id = int(request.match_info['user_id'])

        user = await self.get_object('mail_user',
                                     where={'id': user_id})
        if not user:
            return web.Response(text='User not found', status=404)

        content = b''
        while True:
            data = await request.content.readany()
            if not data:
                break
            content += data

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
                        'mail_user',
                        set={
                            'avatar': avatar_url,
                            'avatar_token': token
                        },
                        where={'id': user_id}
                    )
                )

        client.put_object(Bucket='users',
                          Key='{}/{}'.format(user_id, token),
                          Body=content)
        return web.json_response({'avatar': avatar_url}, status=200)