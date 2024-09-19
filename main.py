from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from config import limiter
from routers import items, system_status, user_management

app = FastAPI(docs_url=None, redoc_url="/docs", openapi_url="/api/openapi.json")
templates = Jinja2Templates(directory="templates")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(items.router)
app.include_router(system_status.router)
app.include_router(user_management.router)

@app.get("/")
def landing_page(request: Request):
    return templates.TemplateResponse("landing_page.html", {"request": request})