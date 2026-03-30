from contextlib import contextmanager

from psycopg2.pool import SimpleConnectionPool


class Database:
    def __init__(self, database_url):
        self.pool = SimpleConnectionPool(minconn=1, maxconn=3, dsn=database_url)

    @contextmanager
    def connection(self):
        conn = self.pool.getconn()
        try:
            with conn:
                with conn.cursor() as cursor:
                    yield cursor
        finally:
            self.pool.putconn(conn)

    def close(self):
        self.pool.closeall()
