import db
from collections import OrderedDict


class BaseMixinView:

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