import psycopg2
import psycopg2.extras
import db
import settings


class DbMixin:

    def erase_db(self, db_table):
        with psycopg2.connect(settings.CONNECTION_STRING) as conn:
            with conn.cursor() as cursor:
                cursor.execute('TRUNCATE {} CASCADE;'.format(db_table))

    def add_db_object(self, db_table, data):
        with psycopg2.connect(settings.CONNECTION_STRING) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    db.build_universal_insert_query(
                        db_table,
                        set=data
                    )
                )
                return cursor.fetchone()

    def list_db_objects(self, db_table):
        with psycopg2.connect(settings.CONNECTION_STRING) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    db.build_universal_select_query(db_table)
                )
                return cursor.fetchall()