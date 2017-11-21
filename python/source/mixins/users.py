from aiohttp import web
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

    async def _fetch_one(self, cursor):
        record = await cursor.fetchone()
        return OrderedDict(zip(self.FIELDS, record))

    async def _fetch_all(self, cursor):
        records = await cursor.fetchall()
        return [OrderedDict(zip(self.FIELDS, record)) for record in records]

    async def list_users(self, request):
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(self.build_universal_select_query('mail_user'))
                data = await self._fetch_all(cursor)
        return web.json_response(data)

    async def retrieve_user(self, request):
        user_id = int(request.match_info['user_id'])
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(self.build_universal_select_query('mail_user',
                                                                       where={'id': user_id}))
                data = await self._fetch_one(cursor)
        return web.json_response(data)

    async def create_user(self, request):
        request_json = await request.json()
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(self.build_universal_insert_query('mail_user',
                                                                       fields=request_json.keys(),
                                                                       values=request_json.values()))
                data = await self._fetch_one(cursor)
        return web.json_response(data, status=201)

    async def update_user(self, request):
        user_id = int(request.match_info['user_id'])
        request_json = await request.json()
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(self.build_universal_update_query('mail_user',
                                                                       set=request_json,
                                                                       where={'id': user_id}))
                data = await self._fetch_one(cursor)
        return web.json_response(data, status=200)

    async def delete_user(self, request):
        user_id = int(request.match_info['user_id'])
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(self.build_universal_delete_query('mail_user',
                                                                       where={'id': user_id}))
        return web.json_response(status=204)
