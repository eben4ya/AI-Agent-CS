from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from sqlalchemy import text

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Load environment variables (DATABASE_URL, GOOGLE_API_KEY, etc.) before importing app modules.
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

from app.agents import run_agent  # noqa: E402
from app.services.supabase_client import SessionLocal  # noqa: E402


def _format_store_profile(row: dict | None) -> str:
    if not row:
        return ""
    lines = []
    for key, value in row.items():
        if value in (None, ""):
            continue
        label = key.replace("_", " ").title()
        lines.append(f"{label}: {value}")
    return "\n".join(lines)


def _format_catalog(rows: Iterable[dict]) -> str:
    snippets = []
    for row in rows:
        sku = row.get("sku")
        name = row.get("name")
        price_cents = row.get("price_cents")
        desc = row.get("description") or ""

        price = f"Rp{(price_cents or 0)/100:,.0f}"
        snippet = f"{name} (SKU: {sku}), Harga: {price}"
        if desc:
            snippet += f" — {desc[:120]}"
        snippets.append(snippet)
    return "\n".join(snippets)


def _load_context_sync() -> tuple[str, str]:
    with SessionLocal() as session:
        store_row = session.execute(
            text("SELECT * FROM store_info WHERE id = 1")
        ).mappings().first()

        catalog_rows = session.execute(
            text(
                "SELECT sku, name, price_cents, description "
                "FROM products ORDER BY created_at DESC LIMIT 25"
            )
        ).mappings().all()

    return _format_store_profile(dict(store_row) if store_row else None), _format_catalog(
        [dict(row) for row in catalog_rows]
    )


async def _load_context() -> tuple[str, str]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _load_context_sync)


async def _run(message: str, session_id: str | None, raw: bool) -> None:
    store_profile, catalog_context = await _load_context()
    result = await run_agent(
        message,
        session_id=session_id,
        store_profile=store_profile,
        catalog_context=catalog_context,
    )

    print("=== Agent Reply ===")
    print(result.get("reply", ""))

    if raw:
        print("\n=== Intermediate Steps ===")
        for step in result.get("intermediate_steps", []):
            print(step)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send a message through the LangChain agent using live services."
    )
    parser.add_argument("message", help="Customer message to test.")
    parser.add_argument(
        "--session",
        help="Optional session/WhatsApp ID to reuse memory between runs.",
        default=None,
    )
    parser.add_argument(
        "--raw",
        help="Print intermediate tool calls returned by the agent.",
        action="store_true",
    )
    args = parser.parse_args()

    asyncio.run(_run(args.message, args.session, args.raw))


if __name__ == "__main__":
    main()
