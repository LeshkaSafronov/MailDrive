import psycopg2

from aiohttp import web
from settings.settings import CONNECTION_STRING
from collections import OrderedDict
from mixins.build import BuildMixin


class UserMixinView(BuildMixin):

    FIELDS = ('id',
              'name',
              'subname',
              'age',
              'country',
              'telephone_number',
              'email',
              'password')

    def _register_routes(self):
        self.router.add_get('/users', self.list_users)
        self.router.add_get('/users/{user_id:\d+}', self.retrieve_user)
        self.router.add_post('/users', self.create_user)
        self.router.add_put('/users/{user_id:\d+}', self.update_user)
        self.router.add_delete('/users/{user_id:\d+}', self.delete_user)

    async def list_users(self, request):
        data = []
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(self.build_universal_select_query('mail_user'))
                for record in await cursor.fetchall():
                    data.append(OrderedDict(zip(self.FIELDS, record)))
        return web.json_response(data)

    async def retrieve_user(self, request):
        user_id = int(request.match_info['user_id'])
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(self.build_universal_select_query('mail_user',
                                                                       where={'id': user_id}))
                record = await cursor.fetchone()
                data = OrderedDict(zip(self.FIELDS, record))
        return web.json_response(data)

    async def create_user(self, request):
        request_json = await request.json()
        with psycopg2.connect(CONNECTION_STRING) as conn:
            with conn.cursor() as cursor:
                cursor.execute(self.build_universal_insert_query('mail_user',
                                                                 fields=request_json.keys(),
                                                                 values=request_json.values()))
                data = cursor.fetchone()
        return web.json_response({'status': 'success'})

    async def update_user(self, request):
        user_id = int(request.match_info['user_id'])
        request_json = await request.json()
        with psycopg2.connect(CONNECTION_STRING) as conn:
            with conn.cursor() as cursor:
                cursor.execute(self.build_universal_update_query('mail_user',
                                                                 set=request_json,
                                                                 where={'id': user_id}))
                data = cursor.fetchone()
        return web.json_response({'status': 'success'})

    async def delete_user(self, request):
        user_id = int(request.match_info['user_id'])
        with psycopg2.connect(CONNECTION_STRING) as conn:
            with conn.cursor() as cursor:
                cursor.execute(self.build_universal_delete_query('mail_user',
                                                                 where={'id': user_id}))
        return web.json_response({'status': 'success'})
