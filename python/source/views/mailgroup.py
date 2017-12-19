from aiohttp import web

import db
import exceptions
from views.base import BaseViewSet
from datetime import datetime


class MailGroupViewSet(BaseViewSet):

    OBJECT_ID = 'mailgroup_id'
    DB_TABLE = 'maildrive_mailgroup'

    def __init__(self, dbpool):
        self._dbpool = dbpool

    def register_routes(self, router):
        router.add_get('/api/mailgroups', self.list_objects)
        router.add_get('/api/mailgroups/{mailgroup_id:\d+}', self.retrieve_object)
        router.add_post('/api/mailgroups', self.create_object)
        router.add_put('/api/mailgroups/{mailgroup_id:\d+}', self.update_object)
        router.add_delete('/api/mailgroups/{mailgroup_id:\d+}', self.delete_object)

        router.add_post('/api/mailgroups/change', self.change)

    async def change(self, request):
        request_data = await request.json()

        for field in ['user_id', 'mail_id', 'mailgroup_id']:
            if field not in request_data:
                raise exceptions.FieldRequired(field)

        for db_name, field_id in [('maildrive_mail', 'mail_id'),
                                  ('maildrive_user', 'user_id'),
                                  ('maildrive_mailgroup', 'mailgroup_id')]:
            entity = await self.get_object(db_name,
                                           where={'id': request_data[field_id]})
            if not entity:
                return web.Response(text='Not found', status=404)

        user_mail = await self.get_object(
            'maildrive_user_mail',
            where={
                'user_id': request_data['user_id'],
                'mail_id': request_data['mail_id']
            }
        )

        if not user_mail:
            return web.Response(text='Not found', status=404)

        async with self._dbpool.acquire() as conn:
            data = await db.exec_universal_update_query(
                'maildrive_user_mail',
                set={
                    'mailgroup_id': request_data['mailgroup_id']
                },
                where={
                    'id': user_mail['id']
                },
                conn=conn
            )
        async with self._dbpool.acquire() as conn:
            await db.exec_universal_insert_query(
                'maildrive_log',
                set={
                    'entity': 'mailgroups',
                    'method': 'change',
                    'timestamp': datetime.now()
                },
                conn=conn
            )
        return web.json_response(data)


