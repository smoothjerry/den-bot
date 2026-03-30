from psycopg2.pool import SimpleConnectionPool


class Database:
    def __init__(self, database_url):
        self.pool = SimpleConnectionPool(minconn=1, maxconn=3, dsn=database_url)

    def get_conn(self):
        return self.pool.getconn()

    def put_conn(self, conn):
        self.pool.putconn(conn)

    def close(self):
        self.pool.closeall()
