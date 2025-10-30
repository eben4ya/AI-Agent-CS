from fastapi import APIRouter, HTTPException

from app.agents import get_conversation_turns, run_agent, default_memory_store
from app.services.supabase_client import get_session

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/reply")
async def agent_reply(body: dict):
    user = body.get("from")
    text = (body.get("text") or "").strip()

    if not user or not text:
        raise HTTPException(status_code=422, detail="Missing required message fields.")

    pool = await get_session()
    async with pool.acquire() as conn:
        store_row = await conn.fetchrow("select name, address, open_hours, phone, city_id from store_info where id=1")
        catalog_rows = await conn.fetch("select sku, name, price_cents, description from products order by created_at desc limit 25")

    store_profile = ""
    if store_row:
        store_profile = "\n".join(
            f"{key.replace('_', ' ').title()}: {value}"
            for key, value in dict(store_row).items()
            if value not in (None, "")
        )

    catalog_context = ""
    if catalog_rows:
        snippets = []
        for row in catalog_rows:
            product = dict(row)
            snippet = f"{product.get('name')} (SKU: {product.get('sku')}), Harga: Rp{product.get('price_cents')/100:,.0f}"
            if product.get("description"):
                snippet += f" — {product['description'][:120]}"
            snippets.append(snippet)
        catalog_context = "\n".join(snippets)

    result = await run_agent(
        text,
        session_id=user,
        store_profile=store_profile,
        catalog_context=catalog_context,
    )

    reply = result.get("reply", "") or "Maaf, saya belum bisa menjawab sekarang. Mohon tunggu sebentar ya."

    async with pool.acquire() as conn:
        await conn.execute(
            "insert into chat_logs (wa_user,direction,message,meta) values ($1,'out',$2,$3)",
            user,
            reply,
            {"agent": "langchain", "intermediate_steps": result.get("intermediate_steps")},
        )

    default_memory_store.append_user_message(user, text)
    default_memory_store.append_ai_message(user, reply)

    return {
        "reply": reply,
        "meta": {
            "intermediate_steps": result.get("intermediate_steps"),
        },
    }
