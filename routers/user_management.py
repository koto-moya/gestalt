from fastapi import HTTPException, Depends, status, Request, Form, Response
from datetime import timedelta
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse


from modules.utils import authenticate_user, create_access_token, get_user, get_current_user, verify_password
from modules.types import Token, NewPasswordPayload, User
from modules.db import get_email, store_reset_token, send_token, reset_password_m, remove_reset_token, reset_authentication_verification,change_password_m
from config import limiter, TOKEN_EXPIRY

router  = APIRouter(prefix= "/account")
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def login(request: Request, response: Response)-> dict:
    response = templates.TemplateResponse("login_page.html", {"request": request}) 
    response.delete_cookie(key="access_token",  path="/")
    return response

@router.get("/resetpasswordpage", response_class=HTMLResponse, include_in_schema=False,)
def login_page(request: Request):
    return templates.TemplateResponse("get_reset_token.html", {"request": request})

@router.post("/token", include_in_schema=False)
@limiter.limit("100/minute")
async def login_for_access_token(request: Request, username: str = Form(...), password: str = Form(...)) -> Token:
    user = authenticate_user(username, password) # datatype: UserInDB
    if not user:
        #raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers ={"WWW-Authenticate": "Bearer"})
        return templates.TemplateResponse("login_page_incorrect_username_or_password.html", {"request":request})
    access_token_expires = timedelta(minutes=TOKEN_EXPIRY/200)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    response = RedirectResponse(url="/upload", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", 
                        value=f"Bearer {access_token}",
                        httponly=True, 
                        samesite="strict",
                        max_age=900) #secure=True, enable in production https  # 50 min token expiry 
    return response

@router.post("/resetpasswordtoken", include_in_schema=False, response_class=HTMLResponse)
@limiter.limit("100/minute")
async def get_reset_token(request: Request,email: str = Form(...)) -> dict:
    email = get_email(email)
    if email:
        store_reset_token(email)
        send_token(email)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No user found with this email")
    return templates.TemplateResponse("reset_password.html", {"request": request})

@router.post("/resetpassword", include_in_schema=False, response_class=HTMLResponse)
@limiter.limit("1/minute")
async def reset_password(request: Request, email: str = Form(...), token: str = Form(...), new_password: str = Form(...)) -> dict:
    check = reset_authentication_verification(email, token)   
    if not check:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email or token not recognized")
    else:
        reset_password_m(email, token, new_password)
    remove_reset_token(email)
    return templates.TemplateResponse("reset_successful.html", {"request": request})

@router.post("/changepassword", include_in_schema=False)
@limiter.limit("1/minute")
async def change_password(request: Request, new_password_payload: NewPasswordPayload, current_user: User =  Depends(get_current_user)) -> dict:
    if current_user.username != new_password_payload.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to change this user's password")
    user = get_user(new_password_payload.username)
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, 
                            detail="Incorrect username", 
                            headers ={"WWW-Authenticate": "Bearer"})
    if verify_password(new_password_payload.new_password, user["hashed_password"]) or not verify_password(new_password_payload.old_password, user["hashed_password"]):
        raise HTTPException(status_code = status.HTTP_406_NOT_ACCEPTABLE, 
                            detail="New password matches old or old password does not match")
    change_password_m(new_password_payload)
    return {"status": "Success"}