from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
from psycopg2 import pool
from psycopg2.extras import RealDictCursor 
from contextlib import contextmanager
import os
from datetime import datetime, timezone, timedelta
from . import types
import secrets
import string
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SECRET_KEY = os.getenv("CRYPTKEY") # generate using openssl rand -hex 32
ALGORITHM = "HS256" # uses SHA-256 has function (like SSH!)
TOKEN_EXPIRY = 30 # 30 mins for now

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create a connection pool for better throughput

db_pool = pool.SimpleConnectionPool(minconn=1, maxconn=10, dbname=os.getenv("DBNAME"), user=os.getenv("PGUSER"), password=os.getenv("PGPASSWORD"), host=os.getenv("PGHOST"), port=os.getenv("PGPORT"))

@contextmanager
def get_db_conn():
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)

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
    
# Get a particular user in the DB
def get_user(username: str):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT * FROM api_users where username = %s', (username,))
            user = cursor.fetchone()
        if user:
            return types.UserInDB(**user)
        else:
            return None

# OAuth methods
def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Core method for authenticating the user
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = types.TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def generate_reset_token():
    characters = string.ascii_letters + string.digits  + string.punctuation
    token = ''.join(secrets.choice(characters) for _ in range(random.randint(16,32)))
    return token

def store_reset_token(email):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("UPDATE api_users SET reset_token = %s WHERE email = %s;", (generate_reset_token(), email,))
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
    body = f"Password Reset Token\n\n{token["reset_token"]}\n\nDO NOT SHARE THIS WITH ANYONE."
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



