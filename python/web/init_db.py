import psycopg2
conn_string = "host='db' dbname='postgres' user='postgres'"

DATA_TABLES = {
    'user': """CREATE TABLE mail_user (
                  id SERIAL PRIMARY KEY,
                  name VARCHAR(256),
                  subname VARCHAR(256),
                  age INTEGER CHECK (age > 0),
                  country VARCHAR(256),
                  telephone_number VARCHAR(32),
                  email VARCHAR(254),
                  password VARCHAR(256)
                );"""
}

def init_db():
    with psycopg2.connect(conn_string) as conn:
        with conn.cursor() as cursor:
            for db_table, sql_create_query in DATA_TABLES.items():
                cursor.execute("""SELECT * FROM pg_tables
                                  WHERE schemaname = 'public' AND 
                                        tablename = '{}'""".format(db_table));
                record = cursor.fetchone()
                if not record:
                    cursor.execute(sql_create_query)

if __name__ == "__main__":
    init_db()
