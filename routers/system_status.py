from fastapi import Request
from fastapi import APIRouter
from config import limiter

router = APIRouter(prefix="/system")

@router.get("/health", include_in_schema=False)
@limiter.limit("1/hour")
async def up_check(request: Request):
    return {"system health":"healthy!"}