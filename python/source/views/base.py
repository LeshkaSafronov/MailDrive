import db
import logging
import exceptions

from aiohttp import web
from collections import OrderedDict


class BaseViewSet:

    async def read_content(self, request):
        content = b''
        while True:
            data = await request.content.readany()
            if not data:
                break
            content += data
        return content

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

    async def validation_request_data(self, request_data, method, object=None):
        validators = {validator.split('validate_')[1]: getattr(self, validator)
                        for validator in dir(self) if validator.startswith('validate_')}
        for field, validator in validators.items():
            if method == 'post' or \
                    (field in request_data and request_data[field] != object[field]):
                await validator(request_data)

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
        request_data = await request.json()

        try:
            await self.validation_request_data(request_data, 'post')
        except exceptions.MailDrive as e:
            return web.Response(text=str(e), status=400)

        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(db.build_universal_insert_query(self.DB_TABLE,
                                                                     set=request_data))

                data = await self._fetch_one(cursor)
        return web.json_response(data, status=201)

    async def update_object(self, request):
        object_id = int(request.match_info[self.OBJECT_ID])

        object = await self.get_object(self.DB_TABLE,
                                       where={'id': object_id})
        if not object:
            return web.Response(text='Not found', status=404)

        request_data = await request.json()

        try:
            await self.validation_request_data(request_data, 'put', object)
        except exceptions.MailDrive as e:
            return web.Response(text=str(e), status=400)


        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(db.build_universal_update_query(self.DB_TABLE,
                                                                     set=request_data,
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