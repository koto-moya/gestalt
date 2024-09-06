from fastapi import HTTPException, Depends, status, FastAPI
from fastapi.security import OAuth2PasswordRequestForm
from psycopg2.extras import RealDictCursor 
import json
from datetime import timedelta
from modules.utils import *
from modules.types import *

app = FastAPI(docs_url=None, redoc_url="/docs", openapi_url="/api/openapi.json")

@app.get("/token/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers ={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=TOKEN_EXPIRY)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")

@app.post("/uploadCodes/", summary="Code upload")
async def data_to_db(payload: DataPayload, current_user: User =  Depends(get_current_user)):
    brand_id = get_or_create_brand(payload.brand)
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("INSERT INTO codes_data_lake (brand_id, json_data, source) VALUES (%s, %s, %s);", (brand_id, json.dumps(payload.data), payload.source))
            db_conn.commit()
    return {"status": "success"}


# Need to create a reset password method.  Need to store the user email so we can send the reset token to them.  
@app.get("/resetpasswordtoken/", include_in_schema=False)
async def get_reset_token(reset_token_payload: ResetTokenPayload):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT email FROM api_users WHERE email = %s;", (reset_token_payload.email, ))
            account = cursor.fetchone()
    if account:
        store_reset_token(account["email"])
        send_token(account["email"])
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No user found with this email")

@app.post("/resetpasssword/", include_in_schema=False)
async def reset_password(reset_password_payload: ResetPasswordPayload):
    with get_db_conn() as db_conn:
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT email FROM api_users WHERE reset_token = %s AND email = %s;", (reset_password_payload.token, reset_password_payload.email,))
            check = cursor.fetchone()
            if not check:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email or token not recognized")
            else:
                cursor.execute("UPDATE api_users SET hashed_password = %s WHERE reset_token = %s AND email = %s;", (get_password_hash(reset_password_payload.new_password),reset_password_payload.token, reset_password_payload.email,))
                db_conn.commit()
    remove_reset_token(reset_password_payload.email)

@app.post("/changepassword/", include_in_schema=False)
async def change_password(new_password_payload: NewPasswordPayload, current_user: User =  Depends(get_current_user)):
    with get_db_conn() as db_conn:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if current_user.username != new_password_payload.username:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to change this user's password")
            cursor.execute('SELECT * FROM api_users WHERE username = %s;', (new_password_payload.username,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Incorrect username", headers ={"WWW-Authenticate": "Bearer"})
            if verify_password(new_password_payload.new_password, user["hashed_password"]) or not verify_password(new_password_payload.old_password, user["hashed_password"]):
                raise HTTPException(status_code = status.HTTP_406_NOT_ACCEPTABLE, detail="New password matches old or old password does not match")
            cursor.execute("UPDATE api_users SET hashed_password = %s WHERE username = %s;", (get_password_hash(new_password_payload.new_password), new_password_payload.username))
            db_conn.commit()
    return {"status": "Success"}