from fastapi import FastAPI,Depends,HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from profile import Profile, UserLogin, UserCreate, CreatePost, Post
from sqlalchemy.orm import Session
from crud import user_create, login, change_post, delete_post, create_post, return_all_posts,get_user_post
from db import engine, SessionLocal,Base
from typing import Annotated, List
from datetime import timedelta
from dotenv import dotenv_values
from authenticated import create_access_token, get_current_user
from models import User
from fastapi.middleware.cors import CORSMiddleware

configure_env = dotenv_values(".env")

ACCESS_TOKEN_EXPIRE_MINUTES = 30

origins = configure_env.get("ALLOWED_ORIGINS",[""])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login/token")
Base.metadata.create_all(bind=engine)
app = FastAPI()

#dependency
def dep_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@app.get('/get-post/{user_id}', response_model=List[Post])
def user_post(user_id:int, db:Session = Depends(dep_db)):

    user_post = get_user_post(user_id=user_id, db=db)

    if user_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return user_post
   

@app.post('/create-profile', response_model=Profile)
def create_profile(user:UserCreate,db:Session = Depends(dep_db)):

    try:
        new_user = user_create(user=user,db=db) 

        if (new_user is None):

            raise HTTPException(status_code=400, detail="An account with this email address already exists.")
        
        return new_user
    
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        )


@app.post('/user/login/token')
def get_user(response:Response,form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db:Session = Depends(dep_db)):
    user = UserLogin(email=form_data.username, password = form_data.password)

    authenticated_user = login(user=user, db=db)

    if authenticated_user is None:
        raise HTTPException(status_code=401, detail="Email or Password is wrong")

    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))

    access_token = create_access_token(data={"sub":authenticated_user.email}, expires_delta=access_token_expires)

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )


    return {"message": "Login successful","email": authenticated_user.email}

@app.post('/user/logout')
def logout(reponse:Response):
    reponse.delete_cookie(key="access_token", path="/", httponly=True)

    return{"message":"Successfully logged out!!"}

@app.put('/post-change/{post_id}', response_model=Post)
def alter_post(post_id:int, new_post:CreatePost ,db:Session = Depends(dep_db),current_user: str = Depends(get_current_user)):

    update_post = change_post(post_id=post_id, new_post=new_post,email=current_user, db=db)

    if(update_post is None):
        raise HTTPException(status_code=404, detail="Post not Found")
    
    if update_post == "forbidden":
        raise HTTPException(status_code=403,detail="You are not authorized to update this post", headers={"WWW-Authenticate": "Bearer"})

    return update_post


@app.post('/create-post',response_model=Post)
async def create_new_post(post:CreatePost, db:Session = Depends(dep_db), current_user: str = Depends(get_current_user)):
    try:

        user = db.query(User).filter(User.email == current_user).first()
        if(user is None):
            raise HTTPException(status_code=401,detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
        
        created_post = create_post(post=post,db=db,user_id=user.id)

        if(created_post is None):
            raise HTTPException(status_code=422,detail="Could not create post. The provided user_id does not exist.")
        return created_post
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    
@app.delete('/post-delete/{post_id}')
def delete(post_id:int, db:Session = Depends(dep_db), current_user: str = Depends(get_current_user)):
    
    post = delete_post(db=db, post_id=post_id, email=current_user)

    if(post is None):
        raise HTTPException(status_code=404, detail="Post not Found")
    
    if(post == "forbidden"):
        raise HTTPException(status_code=403,detail="You are not authorized to delete this post", headers={"WWW-Authenticate": "Bearer"})

    return {"successful":"Post has been Deleted", "post":post}