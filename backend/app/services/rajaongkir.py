from pathlib import Path
from dotenv import load_dotenv
import os, httpx

# Pastikan .env terbaca (ubah path ini jika struktur project berbeda)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

RO_KEY = os.getenv("RAJAONGKIR_KEY")
BASE = os.getenv("RAJAONGKIR_BASE", "https://rajaongkir.komerce.id/api/v1")

def _headers():
    if not RO_KEY or RO_KEY.strip() == "":
        # Fail fast biar gak 401 yang membingungkan
        raise RuntimeError("RAJAONGKIR_KEY tidak ditemukan/ kosong. Set di .env")
    return {
        "key": RO_KEY,
        "Accept": "application/json",
    }

async def get_destinations(search: str | None = None):
    # Hindari kirim "None" sebagai string
    params = {}
    if search and search.strip().lower() != "none":
        params["search"] = search.strip()

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(
            f"{BASE}/destination/domestic-destination",
            headers=_headers(),
            params=params or None,  # None = tanpa query param
        )
        r.raise_for_status()
        return r.json()

async def calculate_cost(origin_id: int, destination_id: int,
                         weight: int, courier: str = "jne"):
    data = {
        "origin": origin_id,
        "destination": destination_id,
        "weight": weight,
        "courier": courier,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            f"{BASE}/calculate/domestic-cost",
            headers={**_headers(), "Content-Type": "application/x-www-form-urlencoded"},
            data=data,
        )
        r.raise_for_status()
        return r.json()
