from model.pointBase import PointTagListlBase, tagToFeild

class LogData(PointTagListlBase):
    class TagKeys:
       keys = ["sid", "uid", "page","type"]
    sid:str
    uid:str
    page:str
    type:str
    
    pageHeight:int = None
    pageWidth:int = None

    ratioX:float = None
    ratioY:float = None

    neutral:float = None
    happy:float = None
    sad:float = None
    angry:float = None
    fearful:float = None
    disgusted:float = None
    surprised:float = None

    scroll:float = None