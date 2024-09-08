from fastapi import Depends, Request
from fastapi import APIRouter


from modules.types import DataPayload, User
from modules.db import get_or_create_brand, insert_data
from modules.utils import get_current_user
from config import limiter

router = APIRouter(prefix="/upload")

@router.post("/codes", summary="Code upload")
@limiter.limit("1/minute")
async def data_to_db(request: Request, payload: DataPayload, current_user: User =  Depends(get_current_user)) -> dict:
    brand_id = get_or_create_brand(payload.brand)
    insert_data(brand_id, payload)
    return {"status": "success"}