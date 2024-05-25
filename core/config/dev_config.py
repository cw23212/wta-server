from contextlib import asynccontextmanager
from fastapi import FastAPI

from util import back, async_util

import logging
logger = logging.getLogger("wta."+__name__)

async def requestUrl():
    host = "http://dev.psj2867.com:8000"    
    path = "/api/collect/"
    url = host + path
    logger.info(f"send to reqeust {url}")
    data = [{
        "uid" : "u1",
        "sid" : "s1",
        "page" : "http://test.com",
        "type" : "eye",
        "scroll" : 0.0,
        "coor-x" : 3.0,
        "coor-y" : 4.0,
    }]
    logger.info("response = %s", await async_util.jsonPost(url,data, debug=True) )

def devPreStart():    
    back.run_async(requestUrl())   
    

def setLogger():
    print("set dev Logger")
    format = '%(levelname)s:%(name)s:   %(message)s'
    # format = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
    
    logging.basicConfig(format=format, level=logging.INFO)  

    logging.getLogger('multipart.multipart').setLevel(logging.INFO)
  
    logging.getLogger('aiohttp.client').setLevel(logging.DEBUG)
    logging.getLogger('wta').setLevel(logging.DEBUG)
    logging.getLogger('wta.core.db').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.DEBUG)
    
    
    