from fastapi import APIRouter
from . import collect, user, data

apiRootRouter = APIRouter()

apiRootRouter.include_router(collect.router, prefix="/collect")
apiRootRouter.include_router(user.router, prefix="/user")
apiRootRouter.include_router(data.router, prefix="/data")