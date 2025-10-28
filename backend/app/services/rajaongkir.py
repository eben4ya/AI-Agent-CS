import os, httpx

RO_KEY = os.getenv("RAJAONGKIR_KEY")
BASE = os.getenv("RAJAONGKIR_BASE", "https://api.rajaongkir.com/starter")

async def cost(origin_city_id: int, destination_city_id: int, weight_grams: int, courier: str="jne"):
    headers = {"key": RO_KEY, "content-type": "application/x-www-form-urlencoded"}
    data = {"origin": origin_city_id, "destination": destination_city_id,
            "weight": weight_grams, "courier": courier}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(f"{BASE}/cost", headers=headers, data=data)
        r.raise_for_status()
        return r.json()
