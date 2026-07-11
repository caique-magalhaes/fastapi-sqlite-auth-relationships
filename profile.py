from pydantic import BaseModel
from typing import List


class CreatePost(BaseModel):
    title:str
    description:str 
    class ConfigDict:
        from_attributes = True

class Post(CreatePost):
    id:int
    user_id:int
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


class UserCreate(UserLogin):
    name:str
    country:str
    city:str

class Profile(BaseModel):
    id:int
    name:str
    country:str
    city:str
    email:str

    class ConfigDict:
        from_attributes = True


