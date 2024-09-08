from config import pwd_context
import string
import secrets
import random

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def generate_reset_token():
    characters = string.ascii_letters + string.digits  + string.punctuation
    token = ''.join(secrets.choice(characters) for _ in range(random.randint(16,32)))
    return token