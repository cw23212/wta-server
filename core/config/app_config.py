from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from . import lifeSpan_config, dev_config



import pathlib
RootFilePath = pathlib.Path("./screenshot")
RootFilePath.mkdir(exist_ok=True)
ImageSuffix = ".png"


def app(debug:bool = False)->FastAPI:
    if debug:
        dev_config.setLogger()
        lifespan = lifeSpan_config.devLifespan 
    else:
        lifespan = lifeSpan_config.prodLifespan

    app = FastAPI(lifespan=lifespan)
    origins = [
        "*",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app