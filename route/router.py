from fastapi import APIRouter
router = APIRouter()


@router.get("/")
def rootTest():
    return "index"
