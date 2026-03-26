import psycopg2


def get_db_conn(database_url):
    return psycopg2.connect(database_url)
