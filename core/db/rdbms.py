from core.secret import db_config
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy import create_engine


import logging
logger = logging.getLogger("wta." + __name__)

import sqlite3
def debugSqlite():
    connection = sqlite3.connect("./tset.sqlite")
    connection.set_trace_callback(logger.debug)
    return connection

# engine = create_engine(db_config.DatabaseUrl, creator=debugSqlite)
engine = create_engine(db_config.DatabaseUrl)

class Base(DeclarativeBase):
    def __repr__(self):
        prop = filter(lambda p: isinstance(p, ColumnProperty), self.__mapper__.iterate_properties)
        keys = [p.key for p in prop]
        prop_values =  { k : getattr(self, k) for k in keys }
        values = ", ".join( sorted( f"{k}={v}" for k,v in prop_values.items() ) )
        return "<{} ({})>".format(self.__class__.__name__, values)
    pass


import model.user
import model.data
def setMeta():
    engine.echo=True
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


import functools
def withSessionA(f):
    @functools.wraps(f)
    async def _f(*args, **kargs):
        with Session(engine, expire_on_commit=False) as session:
            kargs.update({"session":session})
            res = await f(*args, **kargs)
            session.commit()
            return res
    return _f

def withSession(f):
    @functools.wraps(f)
    def _f(*args, **kargs):
        if "session" in kargs:
            return f(*args, **kargs)
        else:
            with Session(engine, expire_on_commit=False) as session:
                kargs.update({"session":session})
                res = f(*args, **kargs)
                session.commit()
                return res
    return _f