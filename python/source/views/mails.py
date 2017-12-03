import db
from aiohttp import web
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
        router.add_delete('/api/users/{user_id:\d+}', self.delete_object)
