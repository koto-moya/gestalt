from fastapi import HTTPException, Depends, status, Request, Form
from datetime import timedelta
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router  = APIRouter(prefix= "/account")
templates = Jinja2Templates(directory="templates")


# Make sure to include get current user in all routes!!