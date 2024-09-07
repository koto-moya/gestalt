from fastapi import HTTPException, Depends, status, FastAPI, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from modules.utils import *
from modules.types import *
from modules.db import *

# Limiter for endpoints

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(docs_url=None, redoc_url="/docs", openapi_url="/api/openapi.json")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/token/")
@limiter.limit("1/minute")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers ={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=TOKEN_EXPIRY)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")

@app.post("/uploadCodes/", summary="Code upload")
@limiter.limit("1/minute")
async def data_to_db(request: Request, payload: DataPayload, current_user: User =  Depends(get_current_user)) -> dict:
    brand_id = get_or_create_brand(payload.brand)
    insert_data(brand_id, payload)
    return {"status": "success"}

@app.get("/resetpasswordtoken/", include_in_schema=False)
@limiter.limit("1/minute")
async def get_reset_token(request: Request, reset_token_payload: ResetTokenPayload) -> dict:
    email = get_email(reset_token_payload.email)
    if email:
        store_reset_token(email)
        send_token(email)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No user found with this email")
    return {"status":"success"}

@app.post("/resetpasssword/", include_in_schema=False)
@limiter.limit("1/minute")
async def reset_password(request: Request, reset_password_payload: ResetPasswordPayload) -> dict:
    check = reset_authentication_verification(reset_password_payload)   
    if not check:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email or token not recognized")
    else:
        reset_password_m(reset_password_payload)
    remove_reset_token(reset_password_payload.email)
    return {"status":"success"}

@app.post("/changepassword/", include_in_schema=False)
@limiter.limit("1/minute")
async def change_password(request: Request, new_password_payload: NewPasswordPayload, current_user: User =  Depends(get_current_user)) -> dict:
    if current_user.username != new_password_payload.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to change this user's password")
    user = get_user(new_password_payload.username)
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Incorrect username", headers ={"WWW-Authenticate": "Bearer"})
    if verify_password(new_password_payload.new_password, user["hashed_password"]) or not verify_password(new_password_payload.old_password, user["hashed_password"]):
        raise HTTPException(status_code = status.HTTP_406_NOT_ACCEPTABLE, detail="New password matches old or old password does not match")
    change_password_m(new_password_payload)
    return {"status": "Success"}