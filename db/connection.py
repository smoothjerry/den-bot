from contextlib import contextmanager

from psycopg2.pool import SimpleConnectionPool


class Database:
    def __init__(self, database_url):
        self.database_url = database_url
        self.pool = SimpleConnectionPool(minconn=1, maxconn=3, dsn=database_url)

    def _ensure_pool(self):
        if self.pool.closed:
            self.pool = SimpleConnectionPool(minconn=1, maxconn=3, dsn=self.database_url)

    @contextmanager
    def connection(self):
        self._ensure_pool()
        conn = self.pool.getconn()
        try:
            if conn.closed:
                self.pool.putconn(conn, close=True)
                conn = self.pool.getconn()
            with conn:
                yield conn
        finally:
            self.pool.putconn(conn)

    def close(self):
        self.pool.closeall()
