from model.pointBase import ExtraModelBase
from model.user import User, Content, Chapter

class addToModel:
    def __init__(self, modelCls):
        self.modelCls = modelCls

    def __call__(self, tCls):
        def _f(s):
            d = s.model_dump()        
            d =  { i: d[i] for i in s.__fields__ }
            return self.modelCls(**d)
        tCls.toModel = _f
        return tCls

@addToModel(User)
class UserSignupRequest(ExtraModelBase):
    name:str

class UserLoginRequest(UserSignupRequest):
    pass

class UserIdRequest(ExtraModelBase):
    id:int

@addToModel(Content)
class ContentRequest(ExtraModelBase):
    name:str
    url:str

@addToModel(Content)
class ContentIdRequest(ExtraModelBase):
    id:int

@addToModel(Chapter)
class ChapterRequest(ExtraModelBase):
    name:str
    url:str

    
@addToModel(Chapter)
class ChpaterIdRequest(ExtraModelBase):
    id:int
