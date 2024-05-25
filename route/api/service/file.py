from core.db import influx
import aiofiles

from typing import Any, List
from sqlalchemy.orm import  Session
from fastapi import UploadFile, HTTPException
from sqlalchemy import Select

from core.db.rdbms import withSession, withSessionA
from core.config.app_config import RootFilePath, ImageSuffix
from model.data import Files

CHUNK_SIZE = 1024 * 1024 

@withSessionA
async def writeFile(sid:str, page:str, file:UploadFile, *, session:Session):
    fileName = sid + ImageSuffix
    f = Files(file=fileName, sid=sid, page=page)    
    session.add(f)
    await _WriteFile(fileName, file)    

async def _WriteFile(fileName:str, file:UploadFile):
    try:        
        filepath = RootFilePath.joinpath(fileName)
        async with aiofiles.open(filepath, 'wb') as f:
            while chunk := await file.read(CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:        
        raise HTTPException(status_code=500, detail='There was an error uploading the file')
    finally:
        await file.close()


@withSession
def getFileByUrl(url:str, session:Session):
    s = Select(Files)\
        .where(Files.page == url)        
    file = session.scalar(s)
    if file == None:
        raise HTTPException(status_code=403, detail="chapter not found")        
    filePath = RootFilePath.joinpath(file.sid + ImageSuffix)
    if not filePath.is_file() :
        raise HTTPException(status_code=403, detail="file not found")        
    return filePath
        

@withSession
def _deletFile(fileE:Files, *, session:Session):
    filePath = RootFilePath.joinpath(fileE.file)
    filePath.unlink(missing_ok=True)
    session.delete(fileE)       
    

@withSession
def deletFile(fileName:str, *, session:Session):  
    fileE = session.get(Files, {"file":str})
    if fileE is None:
        return False
    _deletFile(fileE, session=session)
    return True


@withSession
def deletAllFile(session:Session):
    files = session.query(Files).all()
    for i in files:
        _deletFile(i, session=session)

from core.db import influx
@withSession
def deleteFileNotinInflux(session:Session):
    query= """
        from(bucket: "wta")
    |> range(start: -inf)
    |> filter(fn: (r) => r["_measurement"] == "measurement1")
    |>keep(columns: ["sid"])
    |> group()
    |> unique(column: "sid")
    """
    d = influx.readSync(query)
    sids = [ i["sid"] for i in d ]
    files = session.query(Files).all()
    for i in files:
        if i.sid not in sids:
            _deletFile(i, session=session)
            print(f"delete {i.file}")

