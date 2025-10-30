from fastapi import APIRouter, Query
from app.services.supabase_client import get_session
from app.services.rajaongkir import cost

router = APIRouter(prefix="/shipping", tags=["shipping"])

@router.get("/estimate")
async def shipping_estimate(dest_city_id: int = Query(...),
                            weight_grams: int = Query(1000, ge=1),
                            courier: str = Query("jne")):
    pool = await get_session()
    async with pool.acquire() as conn:
        store = await conn.fetchrow("select city_id from store_info where id=1")
    result = await cost(origin_city_id=store["city_id"],
                        destination_city_id=dest_city_id,
                        weight_grams=weight_grams,
                        courier=courier)
    return result
