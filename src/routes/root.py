from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def read_root():
    return {"message": "Data Transformer API is running"}
