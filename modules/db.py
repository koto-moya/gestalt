from psycopg2.extras import RealDictCursor 
import smtplib
import json
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from .types import UserInDB
from .auth_helpers import get_password_hash, generate_reset_token
from config import get_db_conn



def add_user(username, password):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("INSERT INTO api_users (username, hashed_password) VALUES (%s, %s)", (username, get_password_hash(password),))
            db_conn.commit()

def get_or_create_brand(brand_name: str):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT id FROM brands WHERE brand = %s", (brand_name.lower(),))
            brand = cursor.fetchone()
            if not brand:
                cursor.execute("INSERT INTO brands (brand) VALUES (%s) RETURNING id", (brand_name.lower(),))
                brand = cursor.fetchone()
                db_conn.commit()
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
        
def insert_data(brand_id, payload):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("INSERT INTO codes_data_lake (brand_id, json_data, source) VALUES (%s, %s, %s);", (brand_id, json.dumps(payload.data), payload.source))
            db_conn.commit()

def get_email(email):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT email FROM api_users WHERE email = %s;", (email, ))
            account = cursor.fetchone()
    return account["email"]

def reset_authentication_verification(payload):
    with get_db_conn() as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT email FROM api_users WHERE reset_token = %s AND email = %s;", (payload.token, payload.email,))
            check = cursor.fetchone()
    return check

def change_password_m(payload):
    with get_db_conn() as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("UPDATE api_users SET hashed_password = %s WHERE username = %s;", (get_password_hash(payload.new_password), payload.username))
            db_conn.commit()

def reset_password_m(payload):
    with get_db_conn() as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("UPDATE api_users SET hashed_password = %s WHERE reset_token = %s AND email = %s;", (get_password_hash(payload.new_password),payload.token, payload.email,))
            db_conn.commit()

def store_reset_token(email):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            reset_timer = datetime.now(timezone.utc) + timedelta(minutes=15)
            cursor.execute("UPDATE api_users SET reset_token = %s, reset_timer = %s WHERE email = %s;", (generate_reset_token(),reset_timer, email,))
            db_conn.commit()

def remove_reset_token(email):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("UPDATE api_users SET reset_token = NULL WHERE email = %s;", (email,))
            db_conn.commit()

def send_token(receiver: str):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT reset_token FROM api_users WHERE email = %s;", (receiver,))
            token = cursor.fetchone()
    sender = os.getenv("REPORTING_EMAIL")
    password = os.getenv("REPORTING_EMAIL_PASSWORD")
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['subject'] = "Podscale Password Reset Token"
    body = f'Password Reset Token\n\n{token["reset_token"]}\n\nDO NOT SHARE THIS WITH ANYONE.'
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
    except Exception as e:
        return f"failed to send email: {e}"
    finally:
        server.quit()