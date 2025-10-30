from fastapi import APIRouter, BackgroundTasks
from app.services.supabase_client import get_session

router = APIRouter(prefix="/webhook", tags=["webhook"])

async def _log_incoming(payload: dict):
    pool = await get_session()
    async with pool.acquire() as conn:
        await conn.execute(
            "insert into chat_logs (wa_user,direction,message,meta) values ($1,'in',$2,$3)",
            payload.get("from"), payload.get("text"), payload
        )

@router.post("/whatsapp")
async def wa_incoming(payload: dict, bg: BackgroundTasks):
    bg.add_task(_log_incoming, payload)
    return {"ok": True}
