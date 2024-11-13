from fastapi import HTTPException, Depends, status, Request
from datetime import timedelta
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from config import limiter, TOKEN_EXPIRY
from modules.utils import authenticate_user, create_access_token, get_current_user_internal
from modules.types import User, DataPayload, Token, NewBrand, NewPodcast, NewPodcastBatch, NewCodeBatch
from modules.db import insert_data, get_brand_id, new_brand, new_podcast, new_podcast_batch, new_code_batch

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
async def data_to_db(request: Request, payload: DataPayload, current_user: User =  Depends(get_current_user_internal)) -> dict:
    brand_id = get_brand_id(current_user.brand)
    insert_data(brand_id, payload.source, payload.data)
    return {"status": "success"}

@router.post("/newbrand", summary="data upload")
@limiter.limit("100/minute")
async def new_brand_e(request: Request, payload: NewBrand, current_user: User =  Depends(get_current_user_internal)) -> dict:
    new_brand(payload.brand.lower())
    return {"status": "success"}

@router.post("/newpodcast", summary="data upload")
@limiter.limit("100/minute")
async def new_podcast_e(request: Request, payload: NewPodcast, current_user: User =  Depends(get_current_user_internal)) -> dict:
    new_podcast(payload.podcastname)
    return {"status": "success"}

@router.post("/newpodcastbatch", summary="data upload")
@limiter.limit("100/minute")
async def new_podcast_batch_e(request: Request, payload: NewPodcastBatch, current_user: User =  Depends(get_current_user_internal)) -> dict:
    new_podcast_batch(payload.podcastnames)
    return {"status": "success"}

@router.post("/newcodebatch", summary="data upload")
@limiter.limit("100/minute")
async def new_code_batch_e(request: Request, payload: NewCodeBatch, current_user: User =  Depends(get_current_user_internal)) -> dict:
    new_code_batch(payload.newcodes)
    return {"status": "success"}
