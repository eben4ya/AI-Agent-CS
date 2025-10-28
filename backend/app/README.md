# CS Agent API (FastAPI)

## Setup
- Python 3.11+
- `pip install -r requirements.txt`

Create `.env` (use your Supabase creds):
```

DATABASE_URL=postgresql://postgres:password@db.supabase.co:5432/postgres
RAJAONGKIR_KEY=your_ro_key
RAJAONGKIR_BASE=[https://api.rajaongkir.com/starter](https://api.rajaongkir.com/starter)

```

## Run
```
cd backend

uvicorn app.main:app --reload --port 8000

```

## Endpoints
- `GET /products`, `GET /products/{sku}`
- `GET /store/info`
- `GET /shipping/estimate?dest_city_id=&weight_grams=&courier=jne`
- `POST /webhook/whatsapp`
- `POST /agent/reply`
