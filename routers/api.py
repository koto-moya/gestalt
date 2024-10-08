from fastapi import HTTPException, Depends, status, Request
from datetime import timedelta
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from config import limiter, TOKEN_EXPIRY
from modules.utils import authenticate_user, create_access_token, get_current_user
from modules.types import User, DataPayload, Token
from modules.db import insert_data, get_brand_id

router  = APIRouter(prefix= "/api")
# B sure to add get_current_user to all endpoints except for signing in of course

@router.post("/token")
@limiter.limit("100/minute")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = authenticate_user(form_data.username, form_data.password) # datatype: UserInDB
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers ={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=TOKEN_EXPIRY/200)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")

@router.post("/data", summary="data upload")
@limiter.limit("100/minute")
async def data_to_db(request: Request, payload: DataPayload, current_user: User =  Depends(get_current_user)) -> dict:
    brand_id = get_brand_id(current_user.brand)
    insert_data(brand_id, payload.source, payload.data)
    return {"status": "success"}