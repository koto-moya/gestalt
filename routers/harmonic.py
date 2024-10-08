from fastapi import HTTPException, Depends, status, Request
from datetime import timedelta
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from config import limiter, TOKEN_EXPIRY
from modules.utils import authenticate_user, create_access_token, get_current_user_internal
from modules.types import User, DataPayload, Token
from modules.db import get_brands, get_scope, get_codes, get_podcasts, get_code_use

router  = APIRouter(prefix= "/harmonic")
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

@router.get("/getbrands")
@limiter.limit("10/minute")
async def get_brands_e(request: Request, current_user: User =  Depends(get_current_user_internal)):
    scope = get_scope(current_user.id)
    if scope != "internal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Scope")
    else:
        brands = get_brands()
        return brands

@router.get("/getcodes")
@limiter.limit("10/minute")
async def get_codes_e(request: Request, current_user: User =  Depends(get_current_user_internal)):
    scope = get_scope(current_user.id)
    if scope != "internal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Scope")
    else:
        codes = get_codes()
        return codes

@router.get("/getpodcasts")
@limiter.limit("100/minute")
async def get_codes_e(request: Request, current_user: User =  Depends(get_current_user_internal)):
    scope = get_scope(current_user.id)
    if scope != "internal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Scope")
    else:
        podcasts = get_podcasts()
        return podcasts
        
@router.get("/getperformance")
@limiter.limit("100/minute")
async def get_codes_e(request: Request, current_user: User =  Depends(get_current_user_internal)):
    scope = get_scope(current_user.id)
    if scope != "internal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Scope")
    else:
        query_params = request.query_params
        startdate = query_params.get("startdate")
        enddate = query_params.get("enddate")
        brand = query_params.get("brand")
        podcasts = get_podcasts()
        code_use = get_code_use(startdate, enddate, brand)
        return code_use

        


