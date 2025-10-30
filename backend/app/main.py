from fastapi import Depends,FastAPI
from app.routers import products, store, shipping, agent, webhook
from starlette.middleware.base import BaseHTTPMiddleware
import time, logging

from sqlalchemy.orm import Session
from app.services.supabase_client import get_session

app = FastAPI(title="CS Agent API")

class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        resp = await call_next(request)
        dur = int((time.time()-start)*1000)
        logging.getLogger("uvicorn.access").info("%s %s %s %dms",
            request.method, request.url.path, resp.status_code, dur)
        return resp

app.add_middleware(AccessLogMiddleware)

app.include_router(products.router)
app.include_router(store.router)
app.include_router(shipping.router)
app.include_router(agent.router)
app.include_router(webhook.router)

@app.get("/")

@app.get("/healthz")
def healthz(db: Session = Depends(get_session)):
    # contoh query: db.execute(text("SELECT now()"))
    return {"ok": True}

def root():
    return {"ok": True, "service": "cs-agent-api"}
