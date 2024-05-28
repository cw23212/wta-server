from typing import Any, List
from sqlalchemy.orm import  Session, mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey

from core.db.rdbms import Base



class Chapter(Base):
    __tablename__ = "chapter"
    id: Mapped[int] = mapped_column(default=None, primary_key=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("content.id"))
    name: Mapped[str]
    url: Mapped[str]

class Content(Base):
    __tablename__ = "content"
    id: Mapped[int] = mapped_column(default=None, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    name: Mapped[str]
    url: Mapped[str]
    chapters: Mapped[List[Chapter]] = relationship( cascade="all, delete-orphan",)

    def sortData(self, data, pageKey="page", key="id") -> None:
        chapters = { i.url: i for i in self.chapters }
        def _f(i):
            c = chapters[i[pageKey]]
            return c.id if c else -1
        data.sort(key=_f)
        for i in data:
            c = chapters[i[pageKey]]
            i[key] = c.id if c else -1
        

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=False) # unique
    contents: Mapped[List[Content]] = relationship( cascade="all, delete-orphan",)

    def getChapters(self):
        return sum( [ i.chapters for i in self.contents] , [])
    
