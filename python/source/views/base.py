import db
import exceptions
import psycopg2
import psycopg2.extras

from aiohttp import web


class BaseViewSet:

    async def get_object(self, db_table, where):
        async with self._dbpool.acquire() as conn:
            data = await db.exec_universal_select_query(
                db_table,
                where=where,
                one=True,
                conn=conn
            )
        if data:
            return dict(data)
        else:
            return None

    def get_object_id(self, request):
        object_id = request.match_info[self.PK]
        if object_id.isdigit():
            object_id = int(object_id)
        return object_id

    async def validation_request_data(self, request_data, method, object=None):
        validators = {validator.split('validate_')[1]: getattr(self, validator)
                        for validator in dir(self) if validator.startswith('validate_')}
        for field, validator in validators.items():
            if method == 'post' or \
                    (field in request_data and request_data[field] != object[field]):
                await validator(request_data)

    async def list_objects(self, request):
        query_params = {key: int(value) if value.isdigit() else value
                        for key, value in request.query.items()}
        async with self._dbpool.acquire() as conn:
            data = await db.exec_universal_select_query(
                self.DB_TABLE,
                where=query_params,
                conn=conn
            )
            data = list(map(dict, data))

        return web.json_response(data=data)

    async def retrieve_object(self, request):
        object_id = self.get_object_id(request)
        object = await self.get_object(self.DB_TABLE,
                                       where={self.PK: object_id})
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
            async with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                data = await db.exec_universal_insert_query(
                    self.DB_TABLE,
                    set=request_data,
                    conn=conn
                )
        return web.json_response(dict(data), status=201)

    async def update_object(self, request):
        object_id = self.get_object_id(request)

        object = await self.get_object(self.DB_TABLE,
                                       where={self.PK: object_id})
        if not object:
            return web.Response(text='Not found', status=404)

        request_data = await request.json()

        try:
            await self.validation_request_data(request_data, 'put', object)
        except exceptions.MailDrive as e:
            return web.Response(text=str(e), status=400)


        async with self._dbpool.acquire() as conn:
            data = await db.exec_universal_update_query(
                self.DB_TABLE,
                set=request_data,
                where={self.PK: object_id},
                conn=conn
            )
        return web.json_response(data, status=200)

    async def delete_object(self, request):
        object_id = self.get_object_id(request)
        object = await self.get_object(self.DB_TABLE,
                                       where={self.PK: object_id})
        if not object:
            return web.Response(text='Not found', status=404)

        async with self._dbpool.acquire() as conn:
            await db.exec_universal_delete_query(
                self.DB_TABLE,
                where={self.PK: object_id},
                conn=conn
            )
        return web.json_response(status=204)

    async def get_mailgroup_id(self, user_id, mail_id):
        async with self._dbpool.acquire() as conn:
            record = await db.exec_universal_select_query(
                'maildrive_user_mail',
                where={
                    'user_id': user_id,
                    'mail_id': mail_id
                },
                conn=conn,
                one=True
            )
        return record['mailgroup_id']