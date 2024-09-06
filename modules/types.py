from pydantic import BaseModel, constr
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    id: int
    username: str
    created_at: datetime

class UserInDB(User):
    hashed_password: str

# type for changing password
class NewPasswordPayload(BaseModel):
    username: str
    email: str
    old_password: str
    new_password: str

class ResetTokenPayload(BaseModel):
    email: str

class ResetPasswordPayload(BaseModel):
    email: str
    token: str
    
# This type is for the actual data being sent
class DataPayload(BaseModel):
    brand: constr(min_length=1, max_length=30) # type: ignore
    source: constr(min_length=1, max_length=30) # type: ignore
    data: dict