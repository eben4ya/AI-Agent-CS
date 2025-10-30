from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.services.supabase_client import get_session

router = APIRouter(prefix="/store", tags=["store"])

@router.get("/info")
def get_all_stores(db: Session = Depends(get_session)):
    rows = db.execute(text("SELECT * FROM store_info")).mappings().all()
    return [dict(row) for row in rows] if rows else []

@router.get("/{store_id}")
def get_store_by_id(store_id: int, db: Session = Depends(get_session)):
    row = db.execute(
        text("SELECT * FROM store_info WHERE id = :id"),
        {"id": store_id}
    ).mappings().first()
    return dict(row) if row else {}
