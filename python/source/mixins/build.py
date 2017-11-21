import logging


class BuildMixin:

    def _handle_value(self, value):
        return "'{}'".format(value) if isinstance(value, str) else str(value)

    def _build_where(self, where):
        return 'WHERE {}'.format(
            'AND'.join(['{}={}'.format(key, self._handle_value(value))
                        for key, value in where.items()])
        )

    def _build_set(self, set):
        return 'SET {}'.format(
            ','.join(['{}={}'.format(key, self._handle_value(value))
                      for key, value in set.items()])
        )

    def build_universal_select_query(self, db_table, where=None):
        query = 'SELECT * FROM {}'.format(db_table)
        if where:
            query = '{} {}'.format(query, self._build_where(where))
        query += ';'
        return query

    def build_universal_insert_query(self, db_table, fields, values):
        return 'INSERT INTO {db_table} ({fields}) VALUES ({values}) RETURNING *;'.format(
            db_table=db_table,
            fields=",".join(map(str, fields)).replace("'", ''),
            values=",".join(map(self._handle_value, values))
        )

    def build_universal_update_query(self, db_table, set, where):
        return 'UPDATE {db_table} {set} {where} RETURNING *;'.format(
            db_table=db_table,
            set=self._build_set(set),
            where=self._build_where(where)
        )

    def build_universal_delete_query(self, db_table, where):
        return 'DELETE FROM {} {}'.format(db_table, self._build_where(where))


