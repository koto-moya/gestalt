from psycopg2.extras import RealDictCursor 
import argparse
from psycopg2 import pool
from contextlib import contextmanager
import os

from modules.auth_helpers import get_password_hash
from modules.db import get_user

db_pool_user_creator = pool.SimpleConnectionPool(minconn=1, maxconn=10, dbname=os.getenv("DBNAME"), user=os.getenv("PGUSERCREATOR"), password=os.getenv("PGPASSWORDCREATOR"), host=os.getenv("PGHOST"), port=os.getenv("PGPORT"))

@contextmanager
def get_db_conn():
    conn = db_pool_user_creator.getconn()
    try:
        yield conn
    finally:
        db_pool_user_creator.putconn(conn)

def add_user(username, password, brand, email):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("INSERT INTO api_users (username, hashed_password, brand, email) VALUES (%s, %s, %s, %s)", (username, get_password_hash(password), brand.lower(), email,))
            cursor.execute("INSERT INTO brands (brand) VALUES (%s)", (brand.lower(),))
            db_conn.commit()

def insert_scope(user_id, scope):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("INSERT INTO scopes (user_id, scope) VALUES (%s, %s)", (user_id, scope,))
            db_conn.commit()


def main():
    parser = argparse.ArgumentParser(prog = "AddUser", description="insert default credentials for a brand liason")
    parser.add_argument('-u', '--username', required = True)
    parser.add_argument('-p', '--password', required = True)
    parser.add_argument('-b', '--brand', required = True)
    parser.add_argument('-e', '--email', required = True)
    parser.add_argument('-s', '--scope', required = True)
    args = vars(parser.parse_args())
    add_user(args["username"], args["password"], args["brand"], args["email"])
    user_id = get_user(args["username"])
    insert_scope(user_id.id, args["scope"])


if __name__ == "__main__":
    main()