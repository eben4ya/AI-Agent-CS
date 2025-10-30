from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import bindparam, text
from sqlalchemy.types import JSON

from app.agents import get_conversation_turns, run_agent, default_memory_store
from app.services.supabase_client import get_session

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/reply")
async def agent_reply(body: dict, db: Session = Depends(get_session)):
    user = body.get("from")
    text_in = (body.get("text") or "").strip()

    if not user or not text_in:
        raise HTTPException(status_code=422, detail="Missing required message fields.")

    # --- Query profil toko & katalog (sync) ---
    store_row = db.execute(text("""
        SELECT name, address, open_hours, phone, city_id
        FROM store_info WHERE id = 1
    """)).mappings().first()

    catalog_rows = db.execute(text("""
        SELECT sku, name, price_cents, description
        FROM products
        ORDER BY created_at DESC
        LIMIT 25
    """)).mappings().all()

    store_profile = ""
    if store_row:
        store_profile = "\n".join(
            f"{k.replace('_',' ').title()}: {v}"
            for k, v in dict(store_row).items()
            if v not in (None, "")
        )

    catalog_context = ""
    if catalog_rows:
        snippets = []
        for product in catalog_rows:
            snippet = f"{product.get('name')} (SKU: {product.get('sku')}), Harga: Rp{product.get('price_cents')/100:,.0f}"
            if product.get("description"):
                snippet += f" — {product['description'][:120]}"
            snippets.append(snippet)
        catalog_context = "\n".join(snippets)

    # --- Jalankan agent (async) ---
    result = await run_agent(
        text_in,
        session_id=user,
        store_profile=store_profile,
        catalog_context=catalog_context,
    )
    reply = result.get("reply", "") or "Maaf, saya belum bisa menjawab sekarang. Mohon tunggu sebentar ya."

    # --- Simpan log (sync) ---
    insert_stmt = text("""
        INSERT INTO chat_logs (wa_user, direction, message, meta)
        VALUES (:wa_user, 'out', :message, :meta)
    """).bindparams(bindparam("meta", type_=JSON))

    db.execute(insert_stmt, {
        "wa_user": user,
        "message": reply,
        "meta": {"agent": "langchain", "intermediate_steps": result.get("intermediate_steps")},
    })
    db.commit()

    default_memory_store.append_user_message(user, text_in)
    default_memory_store.append_ai_message(user, reply)

    return {
        "reply": reply,
        "meta": {"intermediate_steps": result.get("intermediate_steps")},
    }
