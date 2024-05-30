from fastapi import APIRouter, Depends, Request, UploadFile, Form
from typing import Any, List, Optional, Annotated

from core.db import influx

import logging
logger = logging.getLogger("wta."+__name__)

from .model.dataModel import LogData
from .service import file as fileService

router = APIRouter()


@router.post("/")
async def collectPost(datas:List[LogData]):
    logger.debug("collect data %s", len(datas))
    await influx.write("wta",  [ i.toPoint() for i in datas] )
    return  "success"

    

@router.post("/screen")
async def screenPost(sid:Annotated[str, Form()],
                    page:Annotated[str, Form()],
                    file: UploadFile,
                    height:Annotated[int, Form()],
                    width:Annotated[int, Form()],):    
    await fileService.writeFile(sid,page, height, width, file)    
    return  "success"