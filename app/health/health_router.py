from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def status_check():
    return {"status": "Service is up and running!"}
