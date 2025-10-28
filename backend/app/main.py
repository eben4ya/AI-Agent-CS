from fastapi import FastAPI
from app.routers import products, store, shipping, agent, webhook

app = FastAPI(title="CS Agent API")

app.include_router(products.router)
app.include_router(store.router)
app.include_router(shipping.router)
app.include_router(agent.router)
app.include_router(webhook.router)

@app.get("/")
def root():
    return {"ok": True, "service": "cs-agent-api"}
