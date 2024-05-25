from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import FileResponse
from typing import Any, List, Optional

import logging
logger = logging.getLogger("wta."+__name__)

router = APIRouter()

from .service import data, userService, file
from .model import userModel

@router.get("/")
async def collectGet():
    a= await data.sumExpressionByPage("")

    return a

@router.get("/screen")
def screenGet(id:int):
    """
    스크린샷
    입력값: 회차 아이디 
    """
    chapterId = userModel.ChpaterIdRequest(id=id)
    chapterUrl = userService.dataGetChapterUrlBy(chapterId)
    filePath = file.getFileByUrl(chapterUrl)
    return FileResponse(filePath)

@router.get("/sumExpression")
async def sumExpression(id:int):
    """
    회차의 
    입력값: 회차 아이디 
    """
    chapterId = userModel.ChpaterIdRequest(id=id)
    chapterUrl = userService.dataGetChapterUrlBy(chapterId)
    a= await data.sumExpressionByPage(chapterUrl)
    return a

@router.get("/pageEyeHeatmap")
async def sumExpression(page:str, width:int|None=10, height:int|None=10):
    try:
        a= await data.pageEyeHeatmap(page, width=width, height=height)
        return a
    except:
        raise HTTPException(status_code=403, detail="page not found")

@router.get("/pageExit")
async def sumExpression(page:str):
    try:
        a= await data.pageExitRate(page)
        return a
    except:
        raise HTTPException(status_code=403, detail="page not found")

        
@router.get("/eye/chapter")
async def chapterEyetracknigRawDataGet(id:int):    
    chapterId = userModel.ChpaterIdRequest(id=id)
    chapterUrl = userService.dataGetChapterUrlBy(chapterId)
    a= await data.rawEyeByPage(chapterUrl)
    return a


@router.get("/main/views")
async def allPageViews(id:int):
    """
    최근 n일 해당 유저 작품들의 전체 조회수, 현재 전체일, 입력 유저 id
    """
    userId = userModel.UserIdRequest(id=id)
    user = userService.getUserAllInfo(userId)
    chapters = user.getChapters()
    a = await data.viewsByPages([ i.url for i in chapters])
    return a

