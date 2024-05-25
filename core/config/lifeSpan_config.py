from . import dev_config
from contextlib import asynccontextmanager, AsyncExitStack
from fastapi import FastAPI


from core.db import influx, rdbms


@asynccontextmanager
async def devLifespan(app: FastAPI):
    # dev_config.devPreStart()
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(influx.startClient())
        # await stack.enter_async_context(rdbms.startDb())
        yield


@asynccontextmanager
async def prodLifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(influx.startClient())
        # await stack.enter_async_context(rdbms.startDb())
        yield
