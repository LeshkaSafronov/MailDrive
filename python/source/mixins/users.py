import psycopg2
import logging

from aiohttp import web
from settings.settings import CONNECTION_STRING


class UserMixinView:

    FIELDS = ('id',
              'name',
              'subname',
              'age',
              'country',
              'telephone_number',
              'email',
              'password')

    async def list_users(self, request):
        data = []
        with psycopg2.connect(CONNECTION_STRING) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT * from mail_user""")
                for record in cursor.fetchall():
                    logging.warning('record --> {}'.format(record))
                    data += dict(zip(self.FIELDS, record))
        return web.json_response(data)

    async def retrieve_user(self, request):
        user_id = int(request.match_info['user_id'])
        with psycopg2.connect(CONNECTION_STRING) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT * from mail_user WHERE id = {}""".format(user_id))
                data = dict(zip(self.FIELDS, cursor.fetchall()))
        return web.json_response(data)

    async def create_user(self, request):
        request_json = await request.json()
        with psycopg2.connect(CONNECTION_STRING) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""INSERT INTO mail_user ({}) VALUES ({}) RETURNING *;""".format(
                    str(list(request_json.keys())).replace("'", '')[1:-1],
                    str(list(request_json.values()))[1:-1]
                ))
                data = cursor.fetchone()
                logging.warning('data --> {}'.format(data))
        return web.json_response({'status': 'success'})

    async def update_user(self, request):
        pass
