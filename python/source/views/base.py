import db
from aiohttp import web
from collections import OrderedDict


class BaseViewSet:

    async def get_object(self, db_table, where):
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    db.build_universal_select_query(
                        db_table,
                        where=where
                    )
                )
                data = await self._fetch_one(cursor)
                return data

    async def _fetch_one(self, cursor):
        record = await cursor.fetchone()
        if record:
            return OrderedDict(zip(self.FIELDS, record))
        else:
            return None

    async def _fetch_all(self, cursor):
        records = await cursor.fetchall()
        return [OrderedDict(zip(self.FIELDS, record)) for record in records]

    async def list_objects(self, request):
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(db.build_universal_select_query(self.DB_TABLE))
                data = await self._fetch_all(cursor)
            return web.json_response(data=data)

    async def retrieve_object(self, request):
        object_id = int(request.match_info[self.OBJECT_ID])
        object = await self.get_object(self.DB_TABLE,
                                       where={'id': object_id})
        if not object:
            return web.Response(text='Not found', status=404)
        else:
            return web.json_response(object)

    async def create_object(self, request):
        request_json = await request.json()
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(db.build_universal_insert_query(self.DB_TABLE,
                                                                     fields=request_json.keys(),
                                                                     values=request_json.values()))

                data = await self._fetch_one(cursor)
        return web.json_response(data, status=201)

    async def update_object(self, request):
        object_id = int(request.match_info[self.OBJECT_ID])

        object = await self.get_object(self.DB_TABLE,
                                       where={'id': object_id})
        if not object:
            return web.Response(text='Not found', status=404)

        request_json = await request.json()
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(db.build_universal_update_query(self.DB_TABLE,
                                                                     set=request_json,
                                                                     where={'id': object_id}))
                data = await self._fetch_one(cursor)
        return web.json_response(data, status=200)

    async def delete_object(self, request):
        object_id = int(request.match_info[self.OBJECT_ID])

        object = await self.get_object(self.DB_TABLE,
                                       where={'id': object_id})
        if not object:
            return web.Response(text='Not found', status=404)

        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    db.build_universal_delete_query(
                        self.DB_TABLE,
                        where={'id': object_id}
                    )
                )
        return web.json_response(status=204)