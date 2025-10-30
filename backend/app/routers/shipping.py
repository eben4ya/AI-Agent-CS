from fastapi import APIRouter, Query
from app.services.rajaongkir import get_destinations, calculate_cost

router = APIRouter(prefix="/shipping", tags=["shipping"])

@router.get("/destinations")
async def list_destinations(q: str | None = Query(None, description="Keyword pencarian kota")):
    # Jika user kirim q=None (string), anggap tidak ada filter
    q_clean = None if (q is None or q.strip().lower() == "none") else q
    return await get_destinations(search=q_clean)

@router.get("/estimate")
async def shipping_estimate(
    origin_city_id: int = Query(419, ge=1),  # Default to Sleman
    dest_city_id: int   = Query(..., ge=1),
    weight_grams: int   = Query(1000, ge=1),
    courier: str        = Query("jne")
):
    return await calculate_cost(
        origin_id=origin_city_id,
        destination_id=dest_city_id,
        weight=weight_grams,
        courier=courier
    )
