from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def main() -> None:
    print(f"Loading .env from: {ENV_PATH}")
    if not ENV_PATH.exists():
        print("⚠️  .env file not found at expected path.")
    else:
        load_dotenv(ENV_PATH)
        print("Loaded .env file.")

    keys_to_check: Iterable[str] = [
        "GOOGLE_API_KEY",
        "DATABASE_URL",
        "RAJAONGKIR_KEY",
        "RAJAONGKIR_BASE",
    ]

    print("\nEnvironment variable check:")
    for key in keys_to_check:
        value = os.getenv(key)
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
