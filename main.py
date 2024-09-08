from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import *
from routers import items, system_status, user_management

app = FastAPI(docs_url=None, redoc_url="/docs", openapi_url="/api/openapi.json")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(items.router)
app.include_router(system_status.router)
app.include_router(user_management.router)