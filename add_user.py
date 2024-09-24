from psycopg2.extras import RealDictCursor 
from modules.db import add_user
from modules.auth_helpers import get_password_hash
import argparse
from psycopg2 import pool
from contextlib import contextmanager
import os

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
            cursor.execute("INSERT INTO api_users (username, hashed_password, brand, email) VALUES (%s, %s, %s, %s)", (username, get_password_hash(password), brand, email,))
            db_conn.commit()



def main():
    parser = argparse.ArgumentParser(prog = "AddUser", description="insert default credentials for a brand liason")
    parser.add_argument('-u', '--username', required = True)
    parser.add_argument('-p', '--password', required = True)
    parser.add_argument('-b', '--brand', required = True)
    parser.add_argument('-e', '--email', required = True)
    args = vars(parser.parse_args())
    add_user(args["username"], args["password"], args["brand"], args["email"])

if __name__ == "__main__":
    main()