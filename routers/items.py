from fastapi import Depends, Request
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse


from modules.types import DataPayload, User
from modules.db import get_or_create_brand, insert_data
from modules.utils import get_current_user
from config import limiter

router = APIRouter(prefix="/upload")
templates = Jinja2Templates(directory="templates")

@router.get("/", include_in_schema=False)
def home_page(request: Request):
    return templates.TemplateResponse("home_page.html", {"request":request})

@router.get("/data_upload", include_in_schema=False)
def home_page(request: Request):
    return templates.TemplateResponse("upload_codes_data.html", {"request":request})


@router.post("/data", summary="data upload")
@limiter.limit("1/minute")
async def data_to_db(request: Request, payload: DataPayload, current_user: User =  Depends(get_current_user)) -> dict:
    brand_id = get_or_create_brand(payload.brand)
    insert_data(brand_id, payload)
    return {"status": "success"}
