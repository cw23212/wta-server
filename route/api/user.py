from fastapi import APIRouter, Depends, Request, HTTPException

from pydantic import BaseModel, Extra

from core.db import influx
from core.db.rdbms import withSession
from model.user import User, Content, Chapter
from .model import userModel
from .service import userService

router = APIRouter()


@router.get("/login")
def loginGet(user:str):
    user = userModel.UserLoginRequest(name=user)
    user = userService.userLogin(user)
    if user == None:
        raise HTTPException(status_code=403, detail="user not found")
    return user

@router.post("/signup")
def signupPost(user:userModel.UserSignupRequest):          
    user = userService.signup(user)
    if user == None:        
        raise HTTPException(status_code=403, detail="user name exist")  
    return user
        
@router.get("/me")
def chapterGet(user:int):
    user = userModel.UserIdRequest(id=user)
    user = userService.getUserAllInfo(user)
    if user == None:
        raise HTTPException(status_code=403, detail="user not found")
    return user    


@router.post("/content")
def contentPost(user:userModel.UserIdRequest, content:userModel.ContentRequest) :
    user = userService.addContent(user, content)
    if user == None:
        raise HTTPException(status_code=403, detail="user not found")    
    return user.contents

@router.delete("/content")
def contentDelete(user:userModel.UserIdRequest, content:userModel.ContentIdRequest) :
    user = userService.deleteContent(user, content)    
    return user.contents
    
@router.post("/chapter")
def chapterPost(user:userModel.UserIdRequest, content:userModel.ContentIdRequest, chapter:userModel.ChapterRequest):
    contents = userService.addChapter(user, content, chapter)
    if user == None:
        raise HTTPException(status_code=403, detail="user not found")    
    return contents.chapters

@router.delete("/chapter")
def chapterDelete(user:userModel.UserIdRequest, content:userModel.ContentIdRequest, chapter:userModel.ChpaterIdRequest) :
    content = userService.deleteChapter(user,content, chapter)
    return content.chapters
    