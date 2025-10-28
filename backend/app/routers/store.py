from fastapi import APIRouter
from app.services.supabase_client import get_pool

router = APIRouter(prefix="/store", tags=["store"])

@router.get("/info")
async def store_info():
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("select * from store_info where id=1")
    return dict(row) if row else {}
