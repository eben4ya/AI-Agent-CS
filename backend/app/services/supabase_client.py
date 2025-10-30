# supabase_client.py
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import NullPool  # aktifkan jika perlu matikan pooling client-side

# Pastikan .env di root project ikut terbaca (mirip versi asyncpg kamu)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# 1) Sumber koneksi:
#    - Prioritas ke DATABASE_URL penuh (kalau sudah ada)
#    - Kalau tidak ada, rakit dari variabel terpisah (user/password/host/port/dbname)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    USER = os.getenv("user")
    PASSWORD = os.getenv("password")
    HOST = os.getenv("host")
    PORT = os.getenv("port", "5432")
    DBNAME = os.getenv("dbname")
    if not all([USER, PASSWORD, HOST, PORT, DBNAME]):
        raise RuntimeError(
            "Konfigurasi DB tidak lengkap. Set DATABASE_URL atau user/password/host/port/dbname di .env"
        )
    # psycopg2 (sync) + sslmode=require untuk Supabase
    DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

# 2) Opsi pooling: gunakan NullPool kalau di belakang ada PgBouncer (transaction/session pooler)
USE_NULLPOOL = os.getenv("SQLALCHEMY_DISABLE_POOL", "false").lower() in {"1", "true", "yes"}

engine_kwargs = {}
# if USE_NULLPOOL:
#     engine_kwargs["poolclass"] = NullPool

# 3) Buat engine & SessionLocal
engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_session():
    """
    Dependency ala FastAPI:
    from fastapi import Depends
    def endpoint(db=Depends(get_session)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection() -> None:
    """Uji koneksi sederhana (SET 1) — aman buat cek cepat."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        print("Connection successful!")

# Opsional: helper raw connection (jarang perlu, tapi ada kalau kamu butuh)
def get_connection():
    return engine.connect()
