from pydantic import BaseModel
from typing import List


class Token(BaseModel):
    access_token: str
    token_type: str


class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    fullname: str

    class Config:
        from_attributes = True


class UserRegistration(BaseModel):
    username: str
    email: str
    password: str
    fullname: str


class UserLogin(BaseModel):
    username: str
    password: str


class PostBase(BaseModel):
    title: str
    content: str

class PostDelete(BaseModel):
    pass


class PostUpdate(PostBase):
    pass


class PostCreate(PostBase):
    title: str
    content: str


class PostResponse(PostBase):
    id: int
    author: UserProfile

    class Config:
        from_attributes = True


class PostWithAuthorResponse(PostResponse):
    author: UserProfile


class LikedPostResponse(BaseModel):
    liked_post: List[PostResponse]

