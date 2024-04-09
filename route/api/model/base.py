
from pydantic import BaseModel, Extra
from core.db_config import data_measurement

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
