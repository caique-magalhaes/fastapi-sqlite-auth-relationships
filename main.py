from fastapi import FastAPI,Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from profile import Profile, UserLogin, UserCreate, CreatePost, Post
from sqlalchemy.orm import Session
from crud import user_create, login, change_user, delete_user, create_post, return_all_posts,get_user_post
from db import engine, SessionLocal,Base
from typing import Annotated, List
from datetime import timedelta
from dotenv import dotenv_values
from authenticated import create_access_token, get_current_user
from models import User

configure_env = dotenv_values(".env")

ACCESS_TOKEN_EXPIRE_MINUTES = 30


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
def get_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db:Session = Depends(dep_db)):
    user = UserLogin(email=form_data.username, password = form_data.password)

    authenticated_user = login(user=user, db=db)

    if authenticated_user is None:
        raise HTTPException(status_code=401, detail="Email or Password is wrong")

    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))

    access_token = create_access_token(data={"sub":authenticated_user.email}, expires_delta=access_token_expires)



    return {"access_token":access_token, "token_type":"bearer"}

@app.put('/user-change/{username}', response_model=Profile)
def alter_user(username:str,user:Profile,db:Session = Depends(dep_db)):

    update_user = change_user(username=username,user=user,db=db)

    if(update_user is None):
        raise HTTPException(status_code=404, detail="User not Found")

    return update_user


@app.post('/create-post',response_model=Post)
async def create_new_post(post:CreatePost, db:Session = Depends(dep_db),current_user: str = Depends(get_current_user)):
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

    
    

@app.delete('/user-delete/{username}')
def delete(username:str,db:Session = Depends(dep_db)):

    deleted_user = delete_user(username=username,db=db)

    if(deleted_user is None):
        raise HTTPException(status_code=404, detail="User not Found")

    return {"successful":"User has been Deleted"}