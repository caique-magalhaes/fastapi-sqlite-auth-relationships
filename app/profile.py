from pydantic import BaseModel
from typing import List
from datetime import datetime


class CreatePost(BaseModel):
    title:str
    description:str
    class ConfigDict:
        from_attributes = True

class LikesPost(BaseModel):
    id_user:int
    id_post:int
    class ConfigDict:
            from_attributes = True

class Post(CreatePost):
    id:int
    user_id:int
    user_name:str
    created_at: datetime
    like_count:int = 0

    class ConfigDict:
        from_attributes = True
class User_Posts(BaseModel):
    name:str
    posts:List[Post]
    class ConfigDict:
        from_attributes = True
class UserLogin(BaseModel):
    email:str
    password:str

class UserMe(BaseModel):
    id:int
    email:str
    username:str
    name:str
    like_post_ids:list[int]
    email_confirmed:bool

class UserCreate(UserLogin):
    name:str
    country:str
    username:str

class Profile(BaseModel):
    id:int
    name:str
    country:str
    email:str

    class ConfigDict:
        from_attributes = True


