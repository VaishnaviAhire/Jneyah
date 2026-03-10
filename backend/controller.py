from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def home():
    return {"message": "Main controller"}

# This will be expanded with other routes