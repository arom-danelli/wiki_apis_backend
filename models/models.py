from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from .database import Base

class API(Base):
    __tablename__ = "apis"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    description = Column(String)
    free = Column(Boolean, default=True)
    documentation = Column(String)
    image = Column(String, nullable=True)
    comments = relationship("Comment", back_populates="api", cascade="all, delete-orphan")
    endpoints = relationship("Endpoint", back_populates="api", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="api", cascade="all, delete-orphan")

class Endpoint(Base):
    __tablename__ = "endpoints"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String)
    method = Column(String)
    description = Column(String)
    api_id = Column(Integer, ForeignKey("apis.id"))
    api = relationship("API", back_populates="endpoints")

class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    api_id = Column(Integer, ForeignKey("apis.id"))
    api = relationship("API", back_populates="likes")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    api_id = Column(Integer, ForeignKey("apis.id"))
    content = Column(String)
    api = relationship("API", back_populates="comments")

class User(SQLAlchemyBaseUserTable, Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
