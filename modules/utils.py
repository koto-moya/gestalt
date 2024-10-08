from fastapi import HTTPException, Depends, status, Request
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timezone, timedelta
from fuzzywuzzy import process

from .types import TokenData
from .db import get_user
from config import SECRET_KEY, ALGORITHM, oauth2_scheme
from .auth_helpers import verify_password


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

async def get_current_user(request: Request):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        token = request.cookies.get("access_token")
        if not token:
            raise credentials_exception
        if token.startswith("Bearer "):
            token = token[len("Bearer "):]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_internal(token: str = Depends(oauth2_scheme)): 
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        if not token:
            raise credentials_exception
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def match_pod_names(x, podcasts: list):
    if x == "Podcast" or x == "podcast":
        return "podcast"
    x = x.replace("The", "")
    x = x.replace(" ", "")
    x = x.replace("show", "")
    x = x.replace("the", "")
    x = x.replace("Show", "")
    x = x.replace("Podcast", "")
    x = x.replace("podcast", "")
    x = x.replace("youtube", "")
    x = x.replace("Youtube", "")
    x = x.replace("newsletter", "")
    x = x.replace("Newsletter", "")
    x = x.replace("and", "")
    x = x.replace("And", "")
    x = x.replace("&", "")
    x = x.replace("'", "")
    best_match = process.extractOne(x, podcasts, score_cutoff=80)
    # eventually: if none then insert into podcast table and return x
    if best_match:
        return best_match[0]
    else:
        return best_match