from fastapi import APIRouter
router = APIRouter(prefix="/webhook", tags=["webhook"])

@router.post("/whatsapp")
async def wa_incoming(payload: dict):
    return {"ok": True}
