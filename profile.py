from pydantic import BaseModel

class Profile(BaseModel):
    name:str
    country:str
    city:str
    
