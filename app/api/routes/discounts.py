# Discounts endpoint
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_discounts():
    return {"message": "Discounts endpoint - to be implemented"}
