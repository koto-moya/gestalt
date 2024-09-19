from fastapi import Depends, Request, UploadFile, File, Form
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import io
import csv

from modules.types import User
from modules.db import get_brand_id, insert_data
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
async def data_to_db(request: Request, file: UploadFile = File(...), source: str = Form(...), current_user: User =  Depends(get_current_user)) -> dict:
    content = await file.read()
    csv_file = io.StringIO(content.decode('utf-8'))
    data = csv.DictReader(csv_file)
    data = [r for r in data]
    brand_id = get_brand_id(current_user.brand)
    insert_data(brand_id, source, data)
    return {"status": "success"}