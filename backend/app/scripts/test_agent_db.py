from __future__ import annotations

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env before importing modules that read environment variables.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.services.supabase_client import get_session  # noqa: E402


async def main() -> None:
    url = os.getenv("DATABASE_URL")
    print(f"DATABASE_URL -> {url}")
    pool = await get_session()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("select current_user, current_database()")
    print("Connected as:", dict(row))


if __name__ == "__main__":
    asyncio.run(main())
