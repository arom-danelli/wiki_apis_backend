from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from fastapi_users import schemas

class EndpointBase(BaseModel):
    url: str
    method: str
    description: str

    model_config = {
        "from_attributes": True
    }

class EndpointCreate(EndpointBase):
    pass

class EndpointUpdate(EndpointBase):
    pass

class Endpoint(EndpointBase):
    id: int

class CommentBase(BaseModel):
    content: str

    model_config = {
        "from_attributes": True
    }

class CommentCreate(CommentBase):
    api_id: int

class Comment(CommentBase):
    id: int
    api_id: int

class LikeBase(BaseModel):
    api_id: int

    model_config = {
        "from_attributes": True
    }

class LikeCreate(LikeBase):
    pass

class Like(LikeBase):
    id: int
    user_id: int

class APIBase(BaseModel):
    name: str
    description: str
    free: bool
    documentation: str
    image: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class APICreate(APIBase):
    endpoints: List[EndpointCreate] = Field(default_factory=list)

class APIUpdate(APIBase):
    pass

class API(APIBase):
    id: int
    comments: List[Comment] = Field(default_factory=list)
    likes: int = 0
    endpoints: List[Endpoint] = Field(default_factory=list)

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

class UserCreate(UserBase, schemas.BaseUserCreate):
    password: str

class UserRead(UserBase, schemas.BaseUser[int]):
    id: int
    is_active: bool
    is_superuser: bool
    is_verified: bool

    class Config:
        orm_mode = True

class UserUpdate(UserBase, schemas.BaseUserUpdate):
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
