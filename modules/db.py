from psycopg2.extras import RealDictCursor 
import json
from datetime import datetime, timezone, timedelta

from .types import UserInDB
from .auth_helpers import get_password_hash, generate_reset_token, send_email_with_token
from config import get_db_conn, db_pool_external_user, db_pool_scope_check, db_pool_user_creator, reporting_db_pool


def update_code_use():
    with get_db_conn(reporting_db_pool) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            pass
def add_user(username, password, brand, email):
    with get_db_conn(db_pool_user_creator) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("INSERT INTO api_users (username, hashed_password, brand, email) VALUES (%s, %s, %s, %s)", (username, get_password_hash(password), brand.lower(), email,))
            cursor.execute("INSERT INTO brands (brand) VALUES (%s)", (brand.lower(),))
            db_conn.commit()

def insert_scope(user_id, scope):
    with get_db_conn(db_pool_user_creator) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("INSERT INTO scopes (user_id, scope) VALUES (%s, %s)", (user_id, scope,))
            db_conn.commit()

def get_scope(user_id):
    with get_db_conn(db_pool_scope_check) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT scope FROM scopes WHERE user_id = %s", (user_id,))
            scope = cursor.fetchone()
    return scope["scope"]

def get_brand_id(brand: str):
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor: 
            cursor.execute("SELECT id FROM brands WHERE lower(brand) = lower(%s)", (brand.lower(),))
            brand = cursor.fetchone()
            return brand['id']

def get_user(username: str):
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM api_users where username = %s', (username,))
            user = cursor.fetchone()
        if user:
            return UserInDB(**user)
        else:
            return None
        
def insert_data(brand_id, source, data):
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("INSERT INTO data_lake (brand_id, json_data, source) VALUES (%s, %s, %s);", (brand_id, json.dumps(data), source))
            db_conn.commit()

def get_email(email):
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT email FROM api_users WHERE lower(email) = lower(%s);", (email, ))
            account = cursor.fetchone()
    return account["email"]

def reset_authentication_verification(email, token):
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT email FROM api_users WHERE lower(email) = lower(%s) AND reset_token = %s;", (email, token,))
            check = cursor.fetchone()
    return check

def change_password_m(payload):
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("UPDATE api_users SET hashed_password = %s WHERE username = %s;", (get_password_hash(payload.new_password), payload.username))
            db_conn.commit()

def reset_password_m(email, token, new_password):
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("UPDATE api_users SET hashed_password = %s WHERE reset_token = %s AND lower(email) = lower(%s);", (get_password_hash(new_password),token, email,))
            db_conn.commit()

def store_reset_token(email):
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            reset_timer = datetime.now(timezone.utc) + timedelta(minutes=15)
            cursor.execute("UPDATE api_users SET reset_token = %s, reset_timer = %s WHERE lower(email) = lower(%s);", (generate_reset_token(),reset_timer, email,))
            db_conn.commit()

def remove_reset_token(email):
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("UPDATE api_users SET reset_token = NULL, reset_timer = NULL WHERE lower(email) = lower(%s);", (email,))
            db_conn.commit()

def send_token(email: str):
    with get_db_conn(db_pool_external_user) as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT reset_token FROM api_users WHERE lower(email) = lower(%s);", (email,))
            token = cursor.fetchone()
    send_email_with_token(email, token["reset_token"])