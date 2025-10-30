# CS Agent API (FastAPI)

## Setup
- Python 3.11+
- `pip install -r requirements.txt`

Create `.env` (use your Supabase creds):
```

GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY_HERE
user=YOUR_DB_USER_HERE 
password=YOUR_DB_PASSWORD_HERE
host=YOUR_DB_HOST
port=YOUR_DB_PORT
dbname=YOUR_DB_NAME_HERE
RAJAONGKIR_KEY=YOUR_RAJAONGKIR_KEY_HERE
RAJAONGKIR_BASE=https://rajaongkir.komerce.id/api/v1/

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
