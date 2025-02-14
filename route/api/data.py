from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import FileResponse
from typing import Any, List, Optional

import logging
logger = logging.getLogger("wta."+__name__)

router = APIRouter()

from .service import data, userService, file as fileService
from .model import userModel

@router.get("/")
async def collectGet():
    a= "data"

    return a

@router.get("/screen/meta")
def screenUrlGet(id:int):
    """
    스크린샷 메타 데이터
    입력값: 회차 아이디 
    """
    chapterId = userModel.ChpaterIdRequest(id=id)
    chapterUrl = userService.dataGetChapterUrlBy(chapterId)
    file = fileService.getFileMeta(chapterUrl)
    return file

@router.get("/screen/image")
def screenImageGet(sid:str):
    """
    스크린샷 주소
    입력값: sid
    """
    filePath = fileService.getFileBySid(sid)
    return FileResponse(filePath)



@router.get("/exp/heatmap")
async def sumExpression(id:int, x=4, y=10):
    """
    회차의 감정 구역별 평균 
    """
    chapterId = userModel.ChpaterIdRequest(id=id)
    chapterUrl = userService.dataGetChapterUrlBy(chapterId)
    a= await data.pageExpHeatmap(chapterUrl, x, y)
    return a

@router.get("/exp/mean/chapter")
async def sumExpression(id:int):
    """
    한 회차의 평균 감정
    입력값: 회차 아이디 
    """
    chapterId = userModel.ChpaterIdRequest(id=id)
    chapterUrl = userService.dataGetChapterUrlBy(chapterId)
    a= await data.meanExpressionByPage(chapterUrl)
    return a

@router.get("/exp/most/page")
async def mostExpScroll(id:int, exp:str):
    """
    회차의 가장 감정이 강한 위치
    입력값: 회차 아이디 
    """
    chapterId = userModel.ChpaterIdRequest(id=id)
    chapterUrl = userService.dataGetChapterUrlBy(chapterId)
    try:  
        file = fileService.getFileMeta(chapterUrl)            
        a= await data.mostExpPage(chapterUrl, exp, file.width, file.height)
        return {"data":a, "file":file}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=403, detail="content not found")
        
@router.get("/exp/most/content")
async def mostExpScrollContent(id:int, exp:str):
    """
    작품의 모든 회차 중 가장 감정이 강한 위치
    입력값: 회차 아이디 
    """
    contentId = userModel.ContentIdRequest(id=id)
    content = userService.getContentById(contentId)
    try:
        chapterUrl = await data.mostExpPageByPages([ i.url for i in content.chapters], exp)          
        file = fileService.getFileMeta(chapterUrl)            
        a= await data.mostExpPage(chapterUrl, exp, file.width, file.height)
        return {"data":a, "file":file}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=403, detail="content not found")

@router.get("/exp/most/happy/page")
async def mostExpScrollHappy(id:int):
    """
    회차의 가장 기쁨이 강한 위치
    입력값: 회차 아이디 
    """
    return await mostExpScroll(id, "기쁨")
        
@router.get("/exp/most/sad/page")
async def mostExpScrollSad(id:int):
    """
    회차의 가장 슬픔이 강한 위치
    입력값: 회차 아이디 
    """
    return await mostExpScroll(id, "슬픔")
        
@router.get("/exp/most/happy/content")
async def mostExpScrollHappyContent(id:int):
    """
    회차의 가장 기쁨이 강한 위치
    입력값: 회차 아이디 
    """
    return await mostExpScrollContent(id, "기쁨")
        
@router.get("/exp/most/sad/content")
async def mostExpScrollSadContent(id:int):
    """
    회차의 가장 슬픔이 강한 위치
    입력값: 회차 아이디 
    """
    return await mostExpScrollContent(id, "슬픔")

@router.get("/eye/heatmap/chapter")
async def eyeHeatmap(id:int, width:int|None=10, height:int|None=10):
    """
    회차의 아이트래킹 히트맵
    입력값: 회차 아이디 
    """
    chapterId = userModel.ChpaterIdRequest(id=id)
    chapterUrl = userService.dataGetChapterUrlBy(chapterId)
    try:    
        a= await data.pageEyeHeatmap(chapterUrl, width=width, height=height)
        return a
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=403, detail="page not found")


        
@router.get("/eye/raw/chapter")
async def chapterEyetracknigRawDataGet(id:int): 
    """
    한 회차의 아이트래킹 전체 정보, 입력 회차 id
    """   
    try:    
        chapterId = userModel.ChpaterIdRequest(id=id)
        chapterUrl = userService.dataGetChapterUrlBy(chapterId)
        a= await data.rawEyeByPage(chapterUrl)
        return a
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=403, detail=str())



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


@router.get("/main/exps")
async def allPageExps(id:int):
    """
    최근 n일 해당 유저 작품들의 평균 감정, 현재 전체일, 입력 유저 id
    """
    userId = userModel.UserIdRequest(id=id)
    user = userService.getUserAllInfo(userId)
    chapters = user.getChapters()
    a = await data.expressionRecentByPages([ i.url for i in chapters])
    return a

@router.get("/main/exit/page")
async def sumExpression(id:int):
    """
    회차의 
    입력값: 회차 아이디 
    """
    chapterId = userModel.ChpaterIdRequest(id=id)
    chapterUrl = userService.dataGetChapterUrlBy(chapterId)
    try:
        a= await data.pageExitRate(chapterUrl)
        return a
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=403, detail="page not found")
    
@router.get("/main/duration/chapter")
async def durationHistrogram(id:int):
    """
    회차의 머문 시간 히스토그램 (0~2, 2~4, 4~6, 5~8, 8+ 분)
    입력값: 회차 아이디 
    """
    chapterId = userModel.ChpaterIdRequest(id=id)
    chapterUrl = userService.dataGetChapterUrlBy(chapterId)
    try:
        a= await data.pageDurationHistogram(chapterUrl)
        return a
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=403, detail="page not found")
    
    
@router.get("/main/duration/content")
async def durationContent(id:int):
    """
    작품의 모든 회차별 머문 시간 평균, 단위 초
    입력값: 작품 아이디 
    """
    contentID = userModel.ContentIdRequest(id=id)
    content = userService.getContentById(contentID)
    try:
        a= await data.durationMeansBy([ i.url for i in content.chapters])
        return a
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=403, detail="content not found")
    
    
@router.get("/main/viewer/content")
async def viewersPerChapter(id:int):
    """
    작품의 회차별 조회수
    입력값: 작품 아이디 
    """
    contentID = userModel.ContentIdRequest(id=id)
    content = userService.getContentById(contentID)
    try:
        a= await data.viewersPerChapter([ i.url for i in content.chapters])
        content.sortData(a)
        return a
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=403, detail="content not found")
    
    
    
@router.get("/main/most/page")
async def mostByPage(id:int):
    """
    회차의 가장 많이 본 위치,
    입력값: 회차 아이디,
    결과: scroll-시작점, height-끝점, 단위-px, 파일
    """
    chapterId = userModel.ChpaterIdRequest(id=id)
    chapterUrl = userService.dataGetChapterUrlBy(chapterId)
    try:  
        file = fileService.getFileMeta(chapterUrl)    
        a= await data.mostScrollByPage(chapterUrl, file.width, file.height)
        return {"data":a, "file":file}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=403, detail="content not found")
    

    
    
@router.get("/main/most/content")
async def mostByContent(id:int):
    """
    작품의 모든 회차 가장 많이 본 위치,
    입력값: 작품 아이디,
    결과: scroll-시작점, height-끝점, 단위-px, 파일
    """
    contentId = userModel.ContentIdRequest(id=id)
    content = userService.getContentById(contentId)
    try:
        chapterUrl = await data.mostScrollPageByPages([ i.url for i in content.chapters])          
        file = fileService.getFileMeta(chapterUrl)            
        a= await data.mostScrollByPage(chapterUrl, file.width, file.height)
        return {"data":a, "file":file}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=403, detail="content not found")
    

 
@router.get("/main/least/page")
async def leastByPage(id:int):
    """
    회차의 가장 적게 본 위치,
    입력값: 회차 아이디,
    결과: scroll-시작점, height-끝점, 단위-px, 파일
    """
    chapterId = userModel.ChpaterIdRequest(id=id)
    chapterUrl = userService.dataGetChapterUrlBy(chapterId)
    try:  
        file = fileService.getFileMeta(chapterUrl)    
        a= await data.leastScrollByPage(chapterUrl, file.width, file.height)
        return {"data":a, "file":file}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=403, detail="content not found")
    

    
    
@router.get("/main/least/content")
async def leastByContent(id:int):
    """
    작품의 모든 회차 가장 많이 본 위치,
    입력값: 작품 아이디,
    결과: scroll-시작점, height-끝점, 단위-px, 파일
    """
    contentId = userModel.ContentIdRequest(id=id)
    content = userService.getContentById(contentId)
    try:
        chapterUrl = await data.leastScrollPageByPages([ i.url for i in content.chapters])          
        file = fileService.getFileMeta(chapterUrl)            
        a= await data.leastScrollByPage(chapterUrl, file.width, file.height)
        return {"data":a, "file":file}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=403, detail="content not found")