from fastapi import APIRouter
router = APIRouter(prefix="/store", tags=["store"])

@router.get("/info")
async def store_info():
    return {}
