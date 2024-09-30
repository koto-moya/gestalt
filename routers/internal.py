from fastapi import HTTPException, Depends, status, Request, Form
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from modules.utils import get_current_user
from modules.types import User
from modules.db import get_scope

router  = APIRouter(prefix= "/internal")
templates = Jinja2Templates(directory="internal_templates")

@router.get("/")
def internal_dashboard(request: Request, current_user: User =  Depends(get_current_user)):
    scope = get_scope(current_user.id)
    if scope != "internal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Scope")
    else:
        return templates.TemplateResponse("dashboard.html", {"request": request}) 
# Make sure to include get current user in all routes!!