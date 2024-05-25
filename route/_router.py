import pathlib

from fastapi import APIRouter
from fastapi.responses import FileResponse
router = APIRouter()


@router.get("/")
def rootTest():
    return "index"

@router.get('/favicon.ico', include_in_schema=False)
async def favicon():
    favicon_path = pathlib.Path().joinpath("route","favicon.ico")    
    return FileResponse(favicon_path)

from route.api import _router as apirouter
router.include_router(apirouter.apiRootRouter, prefix="/api")