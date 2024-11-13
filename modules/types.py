from pydantic import BaseModel, constr
from datetime import datetime
from typing import List, Tuple, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    id: int
    username: str
    created_at: datetime
    brand: str

class ChatMessage(BaseModel):
    new_message: str

class NewCode(BaseModel):
    code: str
    brand: str
    podcast: str
    activestatus: bool
    startdate: str
    enddate: str

class NewCodeBatch(BaseModel):
    newcodes: List[Tuple[str, int, bool, Optional[str], Optional[str], Optional[str], int, Optional[str], Optional[int]]]

class SuspendCode(BaseModel):
    code: str
    podcast: str
    brand: str
    suspenddate: str

class NewPodcast(BaseModel):
    podcastname: str

class NewPodcastBatch(BaseModel):
    podcastnames: List[Tuple[str]]

class NewBrand(BaseModel):
    brand: str

class UserInDB(User):
    hashed_password: str

# type for changing password
class NewPasswordPayload(BaseModel):
    username: str
    email: str
    old_password: str
    new_password: str
    
# This type is for the actual data being sent
class DataPayload(BaseModel):
    source: constr(min_length=1, max_length=30) # type: ignore
    data: dict