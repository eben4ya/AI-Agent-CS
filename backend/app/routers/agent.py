from fastapi import APIRouter
from app.services.supabase_client import get_pool

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/reply")
async def agent_reply(body: dict):
    user = body.get("from")
    text = (body.get("text") or "").lower()

    if "harga" in text or "price" in text:
        reply = "Kirimkan SKU/produk yang ingin dicek ya 🙏"
    elif "jam buka" in text or "buka jam" in text:
        pool = await get_pool()
        async with pool.acquire() as conn:
            s = await conn.fetchrow("select open_hours from store_info where id=1")
            reply = f"Jam buka toko: {s['open_hours']}"
    else:
        reply = "Halo! Saya CS Agent. Tanyakan stok, harga, jam buka, atau ongkir."

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "insert into chat_logs (wa_user,direction,message,meta) values ($1,'out',$2,$3)",
            user, reply, {"rule":"heuristic"}
        )
    return {"reply": reply}
