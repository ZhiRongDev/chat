from fastapi import APIRouter

router = APIRouter(prefix="/user", tags=["api"])


@router.get("/")
async def user():
    return {"message": "user"}
