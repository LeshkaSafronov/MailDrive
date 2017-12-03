import db
import exceptions
import logging

from views.base import BaseViewSet



class MailViewSet(BaseViewSet):

    FIELDS = ('id',
              'header',
              'content',
              'sender_id',
              'recipient_id',
              'is_deleted')

    OBJECT_ID = 'mail_id'
    DB_TABLE = 'mail_mail'

    def __init__(self, dbpool):
        self._dbpool = dbpool

    def register_routes(self, router):
        router.add_get('/api/mails', self.list_objects)
        router.add_get('/api/mails/{mail_id:\d+}', self.retrieve_object)
        router.add_post('/api/mails', self.create_object)
        router.add_put('/api/mails/{mail_id:\d+}', self.update_object)
        router.add_delete('/api/mails/{mail_id:\d+}', self.delete_object)

    async def validate_sender_id(self, request_data):
        if 'sender_id' not in request_data:
            raise exceptions.FieldRequired('sender_id')

        sender_id = request_data.get('sender_id')
        async with self._dbpool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    db.build_universal_select_query(
                        'mail_user',
                        where={
                            'id': sender_id,
                        }
                    )
                )
                data = await cursor.fetchone()
                if not data:
                    raise exceptions.UserDoesNotExists(sender_id)

    async def validate_recipient_id(self, request_data):
        recipient_id = request_data.get('recipient_id')
        if recipient_id is not None:
            async with self._dbpool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        db.build_universal_select_query(
                            'mail_user',
                            where={
                                'id': recipient_id,
                            }
                        )
                    )
                    data = await cursor.fetchone()
                    if not data:
                        raise exceptions.UserDoesNotExists(recipient_id)