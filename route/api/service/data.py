from core.db import influx
import aiofiles
import json

from typing import Any, List
from sqlalchemy.orm import  Session
from fastapi import UploadFile, HTTPException

from core.db.rdbms import withSession, withSessionA


EXPRESSION_LIST = """ ["neutral", "happy", "sad", "angry", "fearful", "disgusted", "surprised"]  """

async def pageExitRate(page, bound = 0.9):
    query = f"""    
base = from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1")
  |> filter(fn: (r) => r["type"] == "scroll"  )  
  |> filter(fn: (r) => r["page"] == "{page}"  )  
  |> max()
  |> group(columns: ["page"])

gt = base 
  |>filter(fn: (r)=>r._value> {bound} , onEmpty: "keep")
  |> count()
  |> set(key: "_field" , value: "gt")

b = base
  |> count()
  |> set(key: "_field" , value: "base")

union(tables: [gt,b])
  |> pivot(rowKey: ["page"],columnKey: ["_field"],  valueColumn: "_value")
    """
    return await influx.read(query)

async def pageEyeHeatmap(page, height:int=10, width:int=10):
    query = f"""    
 import "math"

cw = {height}.0
ch= {width}.0

d = from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1" and  r["type"] == "eye" )  
  |> filter(fn: (r) => r["page"] == "{page}")
  |> keep(columns: ["_time", "_field","_value"])
  |> pivot(rowKey: ["_time"],columnKey: ["_field"],  valueColumn: "_value")
  |> group()
  |> map(fn: (r)=> ({{r with "_value": r["ratioY"]*ch * cw + r["ratioX"]*cw}}))      
  |> histogram(bins: linearBins(count: int(v: cw*ch), start: 0.0, width: 1.0 ))
  |> difference()
  |> map(fn: (r)=> ({{ r with "le":   if math.isInf(f: float(v:  r["le"]), sign: 0)  then  cw*ch  else r["le"]  }}))         
  |> map(fn: (r)=> ({{ r with _value : int(v: r["_value"]) , x : int(v: r["le"]%cw) , y: int(v: r["le"]/cw) }}))

d

    """
    return await influx.read(query)

def sumExpressionByPage(page):
    query = f"""    
        import "array"

base =  from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1")
  |> filter(fn: (r) => r["type"] == "face")
  |> drop(columns: ["start","_stop","_measurement"])
  |> pivot(rowKey: ["_time"],columnKey: ["_field"],  valueColumn: "_value")
  |> group(columns: ["page"])

r = array.map(arr: ["neutral", "happy", "sad", "angry", "fearful", "disgusted", "surprised"] , fn: (x)=>(
    base |> mean(column: x)
    |> duplicate(as: "_value", column: x)
    |> set(key: "exp", value: x)
    |> drop(columns: [x])
))

union(tables: r)
  |> pivot(rowKey: ["page"],columnKey: ["exp"],  valueColumn: "_value")

    """
    return influx.read(query)

    
def sumExpressionByUser(sid):
    query = f"""    
        import "array"

base =  from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1")
  |> filter(fn: (r) => r["type"] == "face")
  |> drop(columns: ["start","_stop","_measurement"])
  |> pivot(rowKey: ["_time"],columnKey: ["_field"],  valueColumn: "_value")

r = array.map(arr: {EXPRESSION_LIST}, fn: (x)=>(
    base |> mean(column: x)
    |> duplicate(as: "_value", column: x)
    |> set(key: "exp", value: x)
    |> drop(columns: [x])
))

union(tables: r)
  |> pivot(rowKey: ["uid"],columnKey: ["exp"],  valueColumn: "_value")

    """
    return influx.read(query)

def rawEyeByPage(page:str):
    query = f"""    

  from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1" and  r["type"] == "eye" )    
  |> filter(fn: (r) => r["page"] == "{page}" )    
  |> pivot(rowKey: ["_time"],columnKey: ["_field"],  valueColumn: "_value")
  |> keep(columns: ["ratioX","ratioY"])
  |> filter(fn: (r) => r["ratioX"] >= 0.0  and r["ratioY"] >= 0.0  )
  |> group()

    """
    return influx.read(query)


def viewsByPage(page:str):
    query = f"""    

  from(bucket: "wta")
    |> range(start: -inf)
    |> filter(fn: (r) => r["_measurement"] == "measurement1")
    |> filter(fn: (r) => r["type"] == "meta"  )  
    |> filter(fn: (r) => r["page"] == "{page}"  )  
    |> keep(columns: ["sid"])
    |> group()
    |> distinct()
    |> count()

    """
    return influx.read(query)

def viewsByPages(pages:List[str]):
    query = f"""    

serises = {json.dumps(pages)}
  from(bucket: "wta")
    |> range(start: -inf)
    |> filter(fn: (r) => r["_measurement"] == "measurement1")
    |> filter(fn: (r) => r["type"] == "meta"  )  
    |> filter(fn: (r) => contains(set: serises , value:  r["page"])  )  
    |> group()
    |> window(every: 1d)
    |> distinct()
    |> count()

    """
    return influx.read(query)




def expressionRecentByPage(page:str):
    query = f"""    


        import "array"

base =  from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1")
  |> filter(fn: (r) => r["type"] == "face")
  |> group()
  |> drop(columns: ["start","_stop","_measurement"])
  |> pivot(rowKey: ["_time"],columnKey: ["_field"],  valueColumn: "_value")

r = array.map(arr: ["neutral", "happy", "sad", "angry", "fearful", "disgusted", "surprised"]   , fn: (x)=>(
    base |> mean(column: x)
    |> duplicate(as: "_value", column: x)    
    |> set(key: "exp", value: x)    
    |> drop(columns: [x])
))

union(tables: r)
   |> pivot(rowKey: [],columnKey: ["exp"],  valueColumn: "_value")


    """
    return influx.read(query)


def mostScrollByPage(page:str):
    query = f"""    
import "array"
import "math"
meta = from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1")
  |> filter(fn: (r) => r["type"] == "meta")
  |> pivot(rowKey: ["sid", "_time"],columnKey: ["_field"],  valueColumn: "_value")
   |> findRecord(fn: (key)=> true, idx:0)

width = float(v: meta["pageWidth"]) 
height = float(v: meta["pageHeight"]) 
nf = (height/width) 
n = int(v: nf )

base = from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1")
  |> filter(fn: (r) => r["type"] == "scroll"  )  
  |> filter(fn: (r) => r["page"] == "http://dev.psj2867.com:8080/test-page/ele.html"  )   
  |> group()

base 
    |> map(fn: (r)=>({{ r with scroll :r["scroll"]* nf  }}))
    |> histogram(bins: linearBins(start: 0.0, width: 1.0, count: n ))
    |> map(fn: (r)=> ({{ r with "le":   if math.isInf(f: float(v:  r["le"]), sign: 0)  then  nf  else r["le"]  }}))         
    |> max()
    |> map(fn: (r)=>({{ r with scroll :r["le"]/nf  , "height": width}}))

    """
    return influx.read(query)