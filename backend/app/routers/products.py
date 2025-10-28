from fastapi import APIRouter, Query
from app.services.supabase_client import get_pool

router = APIRouter(prefix="/products", tags=["products"])

@router.get("")
async def list_products(q: str | None = Query(default=None)):
    pool = await get_pool()
    sql = """
    select p.id, p.sku, p.name, p.description, p.price_cents, p.images, p.category,
           coalesce(
             json_agg(json_build_object('variant',i.variant,'stock',i.stock))
             filter (where i.product_id is not null),'[]'
           ) as inventory
    from products p
    left join inventory i on i.product_id=p.id
    where ($1::text is null or p.name ilike '%'||$1||'%' or p.sku ilike '%'||$1||'%')
    group by p.id
    order by p.created_at desc
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, q)
    return [dict(r) for r in rows]

@router.get("/{sku}")
async def get_by_sku(sku: str):
    pool = await get_pool()
    sql = """
    select p.id, p.sku, p.name, p.description, p.price_cents, p.images, p.category,
           coalesce(
             json_agg(json_build_object('variant',i.variant,'stock',i.stock))
             filter (where i.product_id is not null),'[]'
           ) as inventory
    from products p
    left join inventory i on i.product_id=p.id
    where p.sku=$1
    group by p.id
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, sku)
    return dict(row) if row else {"error": "not_found"}
