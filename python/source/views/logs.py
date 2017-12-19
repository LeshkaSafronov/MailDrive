import db
from .base import BaseViewSet
from aiohttp import web


class LogViewSet(BaseViewSet):

    PK = 'id'
    DB_TABLE = 'maildrive_log'

    def __init__(self, dbpool):
        self._dbpool = dbpool

    def register_routes(self, router):
        router.add_get('/api/logs', self.list_objects)

    async def list_objects(self, request):
        async with self._dbpool.acquire() as conn:
            data = await db.exec_universal_select_query(
                'maildrive_log',
                conn=conn
            )

        data = list(map(dict, data))

        for content in data:
            content['timestamp'] = content['timestamp'].strftime("%Y-%m-%d %H:%M:%S")

        return web.json_response(data=data)