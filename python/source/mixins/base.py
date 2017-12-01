from collections import OrderedDict


class BaseMixinView:

    async def _fetch_one(self, cursor):
        record = await cursor.fetchone()
        if record:
            return OrderedDict(zip(self.FIELDS, record))
        else:
            return None

    async def _fetch_all(self, cursor):
        records = await cursor.fetchall()
        return [OrderedDict(zip(self.FIELDS, record)) for record in records]