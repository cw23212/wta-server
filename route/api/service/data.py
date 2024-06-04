from core.db import influx
import aiofiles
import json

from typing import Any, List
from sqlalchemy.orm import  Session
from fastapi import UploadFile, HTTPException

from core.db.rdbms import withSession, withSessionA
from . import dataUtil

_expression_list =  [
  "기쁨",
  "분노",
  "불안",
  "슬픔",
  "중립",
]
EXPRESSION_LIST = json.dumps(_expression_list, ensure_ascii=False)


async def pageDurationHistogram(page):
    query = f"""    
base = from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1")
  |> filter(fn: (r) => r["type"] == "scroll"  )  
  |> filter(fn: (r) => r["page"] == "{page}"  )  
  |> group(columns: ["sid"])

maxBase = base |> max(column: "_time")
  |> set(key: "_field" , value: "max")

minBase = base |> min(column: "_time")
  |> set(key: "_field" , value: "min")

union(tables: [maxBase, minBase])
  |> pivot(rowKey: ["sid"],columnKey: ["_field"],  valueColumn: "_time")
  |> map(fn: (r)=>({{ r with "_value" :  (uint(v: r["max"]) - uint(v:r["min"]) )/uint(v: 1000000000*60) }}))
   |> map(fn: (r)=>({{ r with "_value" :  float(v: r["_value"]) }})  )
   |> group()
  |> histogram(bins: linearBins(start: 0.0, width: 2.0, count: 4 ))
    |> difference()
    """
    return dataUtil.convertInf(await influx.read(query))


async def durationMeansBy(pages):
    query = f"""    
serises = {json.dumps(pages)}

base = from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1")
  |> filter(fn: (r) => r["type"] == "scroll"  )  
  |> filter(fn: (r) => contains(set: serises , value:  r["page"])  ) 
  |> group(columns: ["sid","page"])

maxBase = base |> max(column: "_time")
  |> set(key: "_field" , value: "max")

minBase = base |> min(column: "_time")
  |> set(key: "_field" , value: "min")

union(tables: [maxBase, minBase])
  |> pivot(rowKey: ["sid","page"],columnKey: ["_field"],  valueColumn: "_time")
  |> map(fn: (r)=>({{ r with "_value" :  (uint(v: r["max"]) - uint(v:r["min"]) )/uint(v: 1000000000) }}))
  |> map(fn: (r)=>({{ r with "_value" :  float(v: r["_value"]) }})  )
  |> group(columns: ["page"])
  |> mean()
   


    """
    return await influx.read(query)


async def viewersPerChapter(pages, bound = 0.9):
    query = f"""    
serises = {json.dumps(pages)}

base = from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1")
  |> filter(fn: (r) => r["type"] == "meta"  )  
  |> filter(fn: (r) => contains(set: serises , value:  r["page"])  ) 
  |> group(columns: ["page"])
  |> distinct(column: "sid")
  |> count()

base

    """
    return await influx.read(query)

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
  |> set(key: "_field" , value: "exit")

b = base
  |> count()
  |> set(key: "_field" , value: "total")

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

async def pageExpHeatmap(page, height:int=4, width:int=10):
    query = f"""    
 import "math"
import "array"

cw = {height}.0
ch= {width}.0

cf = (tables=<-) => {{
rr= array.map(arr: {EXPRESSION_LIST}, fn: (x)=>(
 tables |> mean(column:  x) |> duplicate(column: x , as: "value")  |> set(key: "_field", value: x )
))
r = union(tables: rr)
return r |> pivot(rowKey: ["le"],columnKey: ["_field"],  valueColumn: "value")
}}

d = from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1" and  r["type"] == "face" )  
  |> filter(fn: (r) => r["page"] == "{page}")  
  |> keep(columns: ["_time", "_field","_value"])
  |> pivot(rowKey: ["_time"],columnKey: ["_field"],  valueColumn: "_value")
  |> group()
   |> map(fn: (r)=> ({{ r with "ratioY" : if r["ratioY"] == 1.0 then 0.999999999 else r["ratioY"] }}))
  |> map(fn: (r)=> ({{ r with "ratioX" : if r["ratioX"] == 1.0 then 0.999999999 else r["ratioX"] }}))
  |> map(fn: (r)=> ({{ r with "le": math.floor(x: r["ratioY"]*ch) * cw  + math.floor(x: r["ratioX"]*cw ) }}))      
  |> group(columns: ["le"])
  |> cf()
|> map(fn: (r)=> ({{ r with _value : int(v: r["value"]) , x : math.floor(x: r["le"]%cw) , y: math.floor(x: r["le"]/cw) }}))
 |> map(fn: (r)=> ({{ r with x : (2.0*r["x"]+1.0)/(cw*2.0) , y:  (2.0*r["y"]+1.0)/(ch*2.0)  }}))


d

    """
    print(query)
    return await influx.read(query)

def meanExpressionByPage(page):
    query = f"""    
        import "array"

base =  from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1")
  |> filter(fn: (r) => r["type"] == "face")
  |> filter(fn: (r) => r["page"] == "{page}")
  |> drop(columns: ["start","_stop","_measurement"])
  |> pivot(rowKey: ["_time"],columnKey: ["_field"],  valueColumn: "_value")
  |> group(columns: ["page"])

r = array.map(arr: {EXPRESSION_LIST}, fn: (x)=>(
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

def rawEyeByPage(page:str, n:int = 3000):
    query = f"""    

  from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1" and  r["type"] == "eye" )    
  |> filter(fn: (r) => r["page"] == "{page}" )  
  |> pivot(rowKey: ["_time"],columnKey: ["_field"],  valueColumn: "_value")
  |> keep(columns: ["ratioX","ratioY"])
  |> filter(fn: (r) => r["ratioX"] >= 0.0  and r["ratioY"] >= 0.0  )
  |> group()
  |> tail(n: {n})

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

async def viewsByPages(pages:List[str], day=5):
    query = f"""    

serises = {json.dumps(pages)}
  from(bucket: "wta")
    |> range(start: -{day}d)
    |> filter(fn: (r) => r["_measurement"] == "measurement1")
    |> filter(fn: (r) => r["type"] == "meta"  )  
    |> filter(fn: (r) => contains(set: serises , value:  r["page"])  )  
    |> group()
    |> window(every: 1d)    
    |> count()

    """
    defaultValue = {"_value":0}
    return dataUtil.addRangeDate(await influx.read(query), day, defaultValue)




async def expressionRecentByPages(pages:List[str], day=5):
    query = f"""    
        import "array"
        
serises = {json.dumps(pages)}

base =  from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1")
  |> filter(fn: (r) => r["type"] == "face")
  |> filter(fn: (r) => contains(set: serises , value:  r["page"])  ) 
  |> group()  
  |> pivot(rowKey: ["_time"],columnKey: ["_field"],  valueColumn: "_value")
  |> window(every: 1d)  
  |> tail(n:5)

r = array.map(arr: {EXPRESSION_LIST}   , fn: (x)=>(
    base |> mean(column: x)
    |> duplicate(as: "_value", column: x)    
    |> set(key: "exp", value: x)    
    |> drop(columns: [x])
))

union(tables: r)
   |> pivot(rowKey: [],columnKey: ["exp"],  valueColumn: "_value")
  |> tail(n:5)
   


    """
    print(query)
    defaultValue = { i:0 for i in _expression_list}    
    # return await influx.read(query)
    return dataUtil.addRangeDate(await influx.read(query), day, defaultValue)

    


def mostScrollByPage(page:str, imageWidth:int, imageHeight:int):
    query = f"""    
import "array"
import "math"


width = {imageWidth}.0
height = {imageHeight}.0
nf = (height/width) 
n = int(v: nf )

base = from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1")
  |> filter(fn: (r) => r["type"] == "scroll"  )  
  |> filter(fn: (r) => r["page"] == "{page}"  )   
  |> group()

base 
    |> map(fn: (r)=>({{ r with _value :r["_value"]* nf  }}))
    |> histogram(bins: linearBins(start: 0.0, width: 1.0, count: n ))    
    |> difference()
    |> map(fn: (r)=> ({{ r with "le":   if math.isInf(f: float(v:  r["le"]), sign: 0)  then  nf - 1.0  else r["le"] - 1.0  }}))         
    |> max()
    |> map(fn: (r)=>({{ "start" : int(v: r["le"]/nf*height )  }}))
    |> map(fn: (r)=>({{ r with "end" : r["start"] + {imageWidth} }}))
    

    """
    return influx.read(query)


async def mostScrollPageByPages(pages:List[str]):
    query = f"""    

serises = {json.dumps(pages)}
from(bucket: "wta")
  |> range(start: -inf)
    |> filter(fn: (r) => r["_measurement"] == "measurement1")
    |> filter(fn: (r) => r["type"] == "scroll"  )
    |> filter(fn: (r) => contains(set: serises , value:  r["page"])  )
    |> group(columns: ["page"])
    |> count()
    |> group()
    |> max()
  
    """
    res = await influx.read(query)
    return res[0]["page"]




def leastScrollByPage(page:str, imageWidth:int, imageHeight:int):
    query = f"""    
import "array"
import "math"


width = {imageWidth}.0
height = {imageHeight}.0
nf = (height/width) 
n = int(v: nf )

base = from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1")
  |> filter(fn: (r) => r["type"] == "scroll"  )  
  |> filter(fn: (r) => r["page"] == "{page}"  )   
  |> group()

base 
    |> map(fn: (r)=>({{ r with _value :r["_value"]* nf  }}))
    |> histogram(bins: linearBins(start: 0.0, width: 1.0, count: n ))    
    |> difference()
    |> map(fn: (r)=> ({{ r with "le":   if math.isInf(f: float(v:  r["le"]), sign: 0)  then  nf - 1.0  else r["le"] - 1.0  }}))         
    |> min()
    |> map(fn: (r)=>({{ "start" : int(v: r["le"]/nf*height )  }}))
    |> map(fn: (r)=>({{ r with "end" : r["start"] + {imageWidth} }}))
    

    """
    return influx.read(query)


async def leastScrollPageByPages(pages:List[str]):
    query = f"""    

serises = {json.dumps(pages)}
from(bucket: "wta")
  |> range(start: -inf)
    |> filter(fn: (r) => r["_measurement"] == "measurement1")
    |> filter(fn: (r) => r["type"] == "scroll"  )
    |> filter(fn: (r) => contains(set: serises , value:  r["page"])  )
    |> group(columns: ["page"])
    |> count()
    |> group()
    |> min()
  
    """
    res = await influx.read(query)
    return res[0]["page"]



    
def mostExpPage(page:str, exp:str, imageWidth:int, imageHeight:int):
    query = f"""    
import "array"
import "math"


width = {imageWidth}.0
height = {imageHeight}.0
nf = (height/width) 
n = int(v: nf )

base =  from(bucket: "wta")
  |> range(start: -inf)
  |> filter(fn: (r) => r["_measurement"] == "measurement1")
  |> filter(fn: (r) => r["type"] == "face")
  |> filter(fn: (r) => r["page"] == "{page}"  )   
  |> filter(fn: (r) => r["_field"] == "{exp}" or r["_field"] == "ratioY" )
  |> pivot(rowKey: ["_time"],columnKey: ["_field"],  valueColumn: "_value")
  |> rename(columns: {{"ratioY":"_value"}})
  |> group()

base 
    |> map(fn: (r)=>({{ r with _value : math.floor(x: r["_value"]* nf )  }}))    
    |> group(columns: ["_value"])
    |> mean(column: "{exp}")
    |> group()
    |> max()
    |> map(fn: (r)=>({{ "start" : int(v: r["_value"]/nf*height )  }}))
    |> map(fn: (r)=>({{ r with "end" : r["start"] + {imageWidth} }}))
    

    """    
    return influx.read(query)


async def mostExpPageByPages(pages:List[str], exp:str):
    query = f"""    

serises = {json.dumps(pages)}

  from(bucket: "wta")
  |> range(start: -inf)
    |> filter(fn: (r) => r["_measurement"] == "measurement1")
    |> filter(fn: (r) => r["type"] == "face" )
    |> filter(fn: (r) => r["_field"] == "{exp}" )
    |> filter(fn: (r) => contains(set: serises , value:  r["page"])  )
    |> pivot(rowKey: ["_time"],columnKey: ["_field"],  valueColumn: "_value")
    |> group(columns: ["page"])
    |> mean(column: "{exp}")
    |> group()
    |> max(column: "{exp}")
  
    """
    res = await influx.read(query)
    return res[0]["page"]
