
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import Select

from core.db.rdbms import withSession
from model.user import User, Content, Chapter
from ..model import userModel


@withSession
def addUser(user: User, *,session: Session = None) -> User:
    session.add(user)
    return user

@withSession
def getUser(user: userModel.UserIdRequest, *,session: Session = None) -> User|None:
    s = Select(User)
    d = session.scalar(s)
    return d

@withSession
def getUserByName(name:str, *,session: Session = None) -> User|None:
    s = Select(User)\
        .where(User.name == name)\
        .limit(1)
    d = session.scalar(s)
    return d

@withSession
def getUserAllInfo(user:userModel.UserIdRequest, *, session=Session)-> User|None:
    s = Select(User)\
        .where(User.id == user.id)\
        .options(joinedload(User.contents).selectinload(Content.chapters))
    d = session.scalar(s)
    return d

@withSession
def getUserWithContent(user:userModel.UserIdRequest, *, session=Session):
    s = Select(User)\
        .where(User.id == user.id)\
        .options(joinedload(User.contents))
    d = session.scalar(s)
    return d

# ------------------------

@withSession
def signup(user: userModel.UserSignupRequest, *,session: Session = None):
    if isExistUserName(user, session=session):
        return None
    return addUser(user.toModel(), session=session)

@withSession
def isExistUserName(user: userModel.UserSignupRequest, *,session: Session = None):    
    return getUserByName(user.name, session=session) != None

@withSession
def userLogin(user: userModel.UserLoginRequest, *,session: Session = None) -> User|None:   
    s = Select(User)\
        .where(User.name == user.name)\
        .options(joinedload(User.contents).selectinload(Content.chapters))
    d = session.scalar(s)
    return d


@withSession
def getContent(user:userModel.UserIdRequest, content:userModel.ContentIdRequest,  *,session: Session = None) -> User:    
    s = Select(Content)\
        .where(Content.id == content.id)\
        .where(Content.user_id == user.id)\
        .options(joinedload(Content.chapters))
    d = session.scalar(s)
    return d

@withSession
def getContentById(content:userModel.ContentIdRequest,  *,session: Session = None) -> Content:    
    s = Select(Content)\
        .where(Content.id == content.id)\
        .options(joinedload(Content.chapters))
    d = session.scalar(s)
    return d

# ------------------------

@withSession
def addContent(user:userModel.UserIdRequest, content:userModel.ContentRequest, *,session: Session = None) -> User:    
    user = getUserWithContent(user, session=session)
    if user == None: return None
    user.contents.append(content.toModel())
    return user

@withSession
def deleteContent(user:userModel.UserIdRequest, content:userModel.ContentIdRequest, *,session: Session = None) -> User:    
    userE = getUserAllInfo(user, session=session)
    if userE == None:
        raise HTTPException(status_code=403, detail="user not found")    
    for i in userE.contents:
        if i.id == content.id:
            userE.contents.remove(i)
            return userE
    raise HTTPException(status_code=403, detail="content not found")    

@withSession
def addChapter(user:userModel.UserIdRequest, content:userModel.ContentIdRequest, chapter:userModel.ChapterRequest, *,session: Session = None) -> Content:    
    contents = getContent(user, content, session=session)
    if contents == None: return None
    contents.chapters.append(chapter.toModel())
    return contents
    

@withSession
def deleteChapter(user:userModel.UserIdRequest, content:userModel.ContentIdRequest, chapter:userModel.ChpaterIdRequest, *,session: Session = None) -> User:    
    contents = getContent(user, content, session=session)
    if contents == None:
        raise HTTPException(status_code=403, detail="content not found")    
    for i in contents.chapters:
        if i.id == chapter.id:
            contents.chapters.remove(i)
            return contents
    raise HTTPException(status_code=403, detail="chpater not found")    

# ---------------------------



@withSession
def dataGetChapterUrlBy(chapter:userModel.ChpaterIdRequest, *,session: Session = None) -> str:    
    chapter = session.get(Chapter, {"id":chapter.id})
    if chapter == None:
        raise HTTPException(status_code=403, detail="chapter not found")
    return chapter.url

