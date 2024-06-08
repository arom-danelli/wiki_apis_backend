from typing import List
from pydantic import BaseModel

class EndpointBase(BaseModel):
    url: str
    method: str
    description: str

class EndpointCreate(EndpointBase):
    pass

class Endpoint(EndpointBase):
    id: int

    class Config:
        orm_mode = True

class APIBase(BaseModel):
    name: str
    description: str
    free: bool
    documentation: str

class APICreate(APIBase):
    endpoints: List[EndpointCreate]

class APIUpdate(APIBase):
    pass

class API(APIBase):
    id: int
    endpoints: List[Endpoint] = []
    comments: List['Comment'] = []

    class Config:
        orm_mode = True
        from_attributes = True
        exclude = {'likes'}

class CommentBase(BaseModel):
    api_id: int
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    api_id: int

    class Config:
        orm_mode = True

class LikeBase(BaseModel):
    api_id: int

class LikeCreate(LikeBase):
    pass

class Like(LikeBase):
    id: int

    class Config:
        orm_mode = True
