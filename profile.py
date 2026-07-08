from pydantic import BaseModel
from typing import List


class CreatePost(BaseModel):
    title:str
    description:str 
    user_id:int
    class ConfigDict:
        from_attributes = True

class Post(CreatePost):
    id:int
    class ConfigDict:
        from_attributes = True
    
class User_Posts(BaseModel):
    name:str
    posts:List[Post]

    class ConfigDict:
        from_attributes = True


class User(BaseModel):
    email:str
    password:str


class UserCreate(User):
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


