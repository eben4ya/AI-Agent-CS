from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Load .env before importing modules that read environment variables.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.services.supabase_client import SessionLocal  # noqa: E402


def main() -> None:
    url = os.getenv("DATABASE_URL")
    print(f"DATABASE_URL -> {url}")
    with SessionLocal() as session:
        row = session.execute(text("SELECT current_user, current_database()")).mappings().first()
    print("Connected as:", dict(row) if row else "No result")


if __name__ == "__main__":
    main()
