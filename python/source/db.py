def handle_value(value):
    return "'{}'".format(value) if isinstance(value, str) else str(value)


def build_where(where, sep = ' AND '):
    return 'WHERE {}'.format(
        ' {} '.format(sep).join(['{}={}'.format(key, handle_value(value))
                    for key, value in where.items()])
    )


def build_set(set):
    return 'SET {}'.format(
        ','.join(['{}={}'.format(key, handle_value(value))
                  for key, value in set.items()])
    )


def build_universal_select_query(db_table, where=None, sep=' AND '):
    query = 'SELECT * FROM {}'.format(db_table)
    if where:
        query = '{} {}'.format(query, build_where(where, sep))
    query += ';'
    return query


def build_universal_insert_query(db_table, set):
    return 'INSERT INTO {db_table} ({fields}) VALUES ({values}) RETURNING *;'.format(
        db_table=db_table,
        fields=",".join(map(str, set.keys())).replace("'", ''),
        values=",".join(map(handle_value, set.values()))
    )


def build_universal_update_query(db_table, set, where):
    return 'UPDATE {db_table} {set} {where} RETURNING *;'.format(
        db_table=db_table,
        set=build_set(set),
        where=build_where(where)
    )


def build_universal_delete_query(db_table, where):
    return 'DELETE FROM {} {}'.format(db_table, build_where(where))
