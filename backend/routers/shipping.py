from fastapi import APIRouter
router = APIRouter(prefix="/shipping", tags=["shipping"])

@router.get("/estimate")
async def estimate():
    return {"results": []}
