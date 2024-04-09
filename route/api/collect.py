from fastapi import APIRouter, Depends, Request
from typing import Any, List, Optional

import logging
logger = logging.getLogger("wta."+__name__)

from db import influx
from .model import base

router = APIRouter()

class LogData(base.PointModelBase):
    sid:str
    uid:str
    page:str
    type:str
    scroll:Optional[float] = None  

@router.get("/")
def collectGet():
    return ""

@router.post("/")
async def collectPost(datas:List[LogData]):
    await influx.write("wta",  [ i.toPoint() for i in datas] )
    return  "success"