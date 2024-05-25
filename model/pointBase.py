
from pydantic import BaseModel, Extra
from typing import Optional
from core.secret.db_config import data_measurement

class ExtraModelBase(BaseModel):
    class Config:
        extra = 'allow'


class PointModelBase(BaseModel):
    class Config:
        extra = 'allow'

    def toPoint(self):   
        d = self.model_dump()        
        tags =  { i: d[i] for i in self.__fields__ }
        fields =  self.model_extra 
        point = {
            "measurement" : data_measurement,
            "tags" : tags,
        }
        if "time" in fields:
            _time = fields["time"]
            fields.pop("time")
            point.update({
                "time" : _time,
                "fields" : fields
            })
        else:
            point.update({
                "fields" : fields
            })
        return point

class PointTagListlBase(BaseModel):

    class Config:
        extra = 'allow'

    def toPoint(self):   
        tagKeys = self.TagKeys.keys
        d = self.model_dump()
        d =  { k:v for k,v in d.items() if v is not None }
        tags =  { k:v for k,v in d.items() if k in tagKeys }
        fields =  { k:v for k,v in d.items() if k not in tagKeys }
        point = {
            "measurement" : data_measurement,
            "tags" : tags,
        }
        
        if "time" in fields:
            _time = fields["time"]
            fields.pop("time")
            point.update({
                "time" : _time,
                "fields" : fields
            })
        else:
            point.update({
                "fields" : fields
            })
        return point

def tagToFeild(d, key):    
    d["fields"][key] = d["tags"][key]
    d["tags"].pop(key)
    return d