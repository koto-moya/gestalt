from psycopg2.extras import RealDictCursor 
import json
from datetime import datetime, timezone, timedelta
from .types import UserInDB
from .auth_helpers import get_password_hash, generate_reset_token, send_email_with_token
from config import get_db_conn

def add_user(username, password, brand, email):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("INSERT INTO api_users (username, hashed_password, brand, email) VALUES (%s, %s, %s, %s)", (username, get_password_hash(password), brand, email,))
            db_conn.commit()

def get_brand_id(brand_name: str):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # This should be a little smarter to recognize some more variability in the spelling
            # Now that I think about it, adding a user should be only available internally.
            # i.e. admin needs to add email and brand which will send reset token to the end user
            # like a Brand liason.  
            cursor.execute("SELECT id FROM brands WHERE lower(brand) = lower(%s)", (brand_name,))
            brand = cursor.fetchone()
            # if not brand:
            #     cursor.execute("INSERT INTO brands (brand) VALUES (%s) RETURNING id", (brand_name.lower(),))
            #     brand = cursor.fetchone()
            #     db_conn.commit()
            return brand['id']

def get_user(username: str):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM api_users where username = %s', (username,))
            user = cursor.fetchone()
        if user:
            return UserInDB(**user)
        else:
            return None
        
def insert_data(brand_id, source, data):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("INSERT INTO data_lake (brand_id, json_data, source) VALUES (%s, %s, %s);", (brand_id, json.dumps(data), source))
            db_conn.commit()

def get_email(email):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT email FROM api_users WHERE lower(email) = lower(%s);", (email, ))
            account = cursor.fetchone()
    return account["email"]

def reset_authentication_verification(email, token):
    with get_db_conn() as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT email FROM api_users WHERE lower(email) = lower(%s) AND reset_token = %s;", (email, token,))
            check = cursor.fetchone()
    return check

def change_password_m(payload):
    with get_db_conn() as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("UPDATE api_users SET hashed_password = %s WHERE username = %s;", (get_password_hash(payload.new_password), payload.username))
            db_conn.commit()

def reset_password_m(email, token, new_password):
    with get_db_conn() as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("UPDATE api_users SET hashed_password = %s WHERE reset_token = %s AND lower(email) = lower(%s);", (get_password_hash(new_password),token, email,))
            db_conn.commit()

def store_reset_token(email):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            reset_timer = datetime.now(timezone.utc) + timedelta(minutes=15)
            cursor.execute("UPDATE api_users SET reset_token = %s, reset_timer = %s WHERE lower(email) = lower(%s);", (generate_reset_token(),reset_timer, email,))
            db_conn.commit()

def remove_reset_token(email):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("UPDATE api_users SET reset_token = NULL, reset_timer = NULL WHERE lower(email) = lower(%s);", (email,))
            db_conn.commit()

def send_token(email: str):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT reset_token FROM api_users WHERE lower(email) = lower(%s);", (email,))
            token = cursor.fetchone()
    send_email_with_token(email, token["reset_token"])