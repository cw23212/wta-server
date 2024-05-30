from typing import Any, List
from sqlalchemy.orm import  Session, mapped_column, Mapped, relationship

from core.db.rdbms import Base

class Files(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(default=None, primary_key=True)
    file: Mapped[str] = mapped_column(unique=True)
    sid: Mapped[str]
    page: Mapped[str]
    width: Mapped[int] = mapped_column(nullable=True)
    height: Mapped[int] = mapped_column(nullable=True)

