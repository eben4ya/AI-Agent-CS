from fastapi import APIRouter
router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/reply")
async def agent_reply(body: dict):
    return {"reply": "Hello from Agent skeleton"}
