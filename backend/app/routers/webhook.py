from fastapi import APIRouter, BackgroundTasks
from sqlalchemy import text
from app.services.supabase_client import SessionLocal  # pastikan diekspor di supabase_client

router = APIRouter(prefix="/webhook", tags=["webhook"])

def _log_incoming(payload: dict):
    db = SessionLocal()
    try:
        db.execute(text("""
            INSERT INTO chat_logs (wa_user, direction, message, meta)
            VALUES (:wa_user, 'in', :message, :meta)
        """), {
            "wa_user": payload.get("from"),
            "message": payload.get("text"),
            "meta": payload,
        })
        db.commit()
    finally:
        db.close()

@router.post("/whatsapp")
async def wa_incoming(payload: dict, bg: BackgroundTasks):
    bg.add_task(_log_incoming, payload)
    return {"ok": True}
