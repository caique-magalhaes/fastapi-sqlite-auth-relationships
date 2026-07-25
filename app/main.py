from fastapi import FastAPI,Depends,HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.profile import Profile, UserLogin, UserCreate, CreatePost, Post
from sqlalchemy.orm import Session
from app.crud import user_create, login, change_post, delete_post, create_post, return_all_posts,get_user_post
from app.core.db import engine, SessionLocal,Base, dep_db
from app.routers.user import router as router_user
from app.routers.posts import router as router_posts
from typing import Annotated, List

from datetime import timedelta
from dotenv import dotenv_values
from app.core.authenticated import create_access_token, get_current_user
from app.models import User
from fastapi.middleware.cors import CORSMiddleware


configure_env = dotenv_values(".env")

ACCESS_TOKEN_EXPIRE_MINUTES = 30

origins = configure_env.get("ALLOWED_ORIGINS",[""])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login/token")
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
