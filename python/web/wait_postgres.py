import psycopg2
import logging
import sys
import time

conn_string = "host='db' dbname='postgres' user='postgres'"


def wait_postgres(table_name):
    while True:
        try:
            with psycopg2.connect(conn_string) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("select * from {};".format(table_name))
            logging.warning('Connected!')
            break
        except (psycopg2.OperationalError, psycopg2.ProgrammingError) as e:
            logging.warning(str(e))
        time.sleep(5)


if __name__ == '__main__':
    table_name = sys.argv[1]
    wait_postgres(table_name)