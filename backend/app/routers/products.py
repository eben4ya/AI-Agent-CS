from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.services.supabase_client import get_session

router = APIRouter(prefix="/products", tags=["products"])

@router.get("")
def list_products(
    q: str | None = Query(default=None),
    db: Session = Depends(get_session),
):
    sql = text("""
    SELECT
      p.id, p.sku, p.name, p.description, p.price_cents, p.images, p.category,
      COALESCE(
        json_agg(json_build_object('variant', i.variant, 'stock', i.stock))
        FILTER (WHERE i.product_id IS NOT NULL),
        '[]'::json
      ) AS inventory
    FROM products p
    LEFT JOIN inventory i ON i.product_id = p.id
    WHERE (:q IS NULL OR p.name ILIKE '%' || :q || '%' OR p.sku ILIKE '%' || :q || '%')
    GROUP BY p.id
    ORDER BY p.created_at DESC
    """)
    rows = db.execute(sql, {"q": q}).mappings().all()
    return [dict(r) for r in rows]

@router.get("/{sku}")
def get_by_sku(
    sku: str,
    db: Session = Depends(get_session),
):
    sql = text("""
    SELECT
      p.id, p.sku, p.name, p.description, p.price_cents, p.images, p.category,
      COALESCE(
        json_agg(json_build_object('variant', i.variant, 'stock', i.stock))
        FILTER (WHERE i.product_id IS NOT NULL),
        '[]'::json
      ) AS inventory
    FROM products p
    LEFT JOIN inventory i ON i.product_id = p.id
    WHERE p.sku = :sku
    GROUP BY p.id
    """)
    row = db.execute(sql, {"sku": sku}).mappings().first()
    return dict(row) if row else {"error": "not_found"}
