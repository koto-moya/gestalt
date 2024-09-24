from contextlib import contextmanager
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
import os

db_pool_external_user = pool.SimpleConnectionPool(minconn=1, maxconn=10, dbname=os.getenv("DBNAME"), user=os.getenv("PGUSERSCOPE"), password=os.getenv("PGPASSWORDSCOPE"), host=os.getenv("PGHOST"), port=os.getenv("PGPORT"))

@contextmanager
def get_db_conn():
    conn = db_pool_external_user.getconn()
    try:
        yield conn
    finally:
        db_pool_external_user.putconn(conn)

def get_scope(user_id):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT scope FROM scopes WHERE user_id = %s", (user_id,))
            scope = cursor.fetchone()
    return scope["scope"]