from fastapi import FastAPI,Depends
from fastapi.security import OAuth2PasswordBearer
from app.profile import Post
from sqlalchemy.orm import Session
from app.crud import return_all_posts
from app.core.db import engine,Base, dep_db
from app.routers.user import router as router_user
from app.routers.posts import router as router_posts

from typing import List

from dotenv import dotenv_values
from fastapi.middleware.cors import CORSMiddleware


configure_env = dotenv_values(".env")

origins = configure_env.get("ALLOWED_ORIGINS",[""])

Base.metadata.create_all(bind=engine)
app = FastAPI()


app.include_router(router_user)
app.include_router(router_posts)

#middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)
    


@app.get('/',response_model=List[Post])
def index(db:Session = Depends(dep_db)):
    
    return return_all_posts(db=db)
