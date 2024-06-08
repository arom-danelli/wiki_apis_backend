from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class API(Base):
    __tablename__ = "apis"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    free = Column(Boolean, default=True)
    documentation = Column(String)
    comments = relationship("Comment", back_populates="api")
    endpoints = relationship("Endpoint", back_populates="api")


class Endpoint(Base):
    __tablename__ = "endpoints"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    method = Column(String)
    description = Column(String)
    api_id = Column(Integer, ForeignKey("apis.id"))

    api = relationship("API", back_populates="endpoints")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("apis.id"))


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("apis.id"))
    content = Column(String)

    api = relationship("API", back_populates="comments")
