from slowapi import Limiter
from slowapi.util import get_remote_address
from psycopg2 import pool
import os
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from contextlib import contextmanager

limiter = Limiter(key_func=get_remote_address)

db_pool = pool.SimpleConnectionPool(minconn=1, maxconn=10, dbname=os.getenv("DBNAME"), user=os.getenv("PGUSER"), password=os.getenv("PGPASSWORD"), host=os.getenv("PGHOST"), port=os.getenv("PGPORT"))

@contextmanager
def get_db_conn():
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)

SECRET_KEY = os.getenv("CRYPTKEY") # generate using openssl rand -hex 32
ALGORITHM = "HS256" # uses SHA-256 has function (like SSH!)
TOKEN_EXPIRY = 30 # Cookie creation sees this as seconds so multiply max_age by like 100?

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")