from fastapi import FastAPI,Depends,HTTPException
from profile import Profile, User, UserCreate, CreatePost, Post
from sqlalchemy.orm import Session
from crud import user_create, login, change_user, delete_user, create_post
from db import engine, SessionLocal,Base
from typing import List

Base.metadata.create_all(bind=engine)
app = FastAPI()

#dependency
def dep_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    


@app.get('/')
def init():
    return {"Hello":"World"}

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


@app.post('/user/login')
def get_user(user:User,db:Session = Depends(dep_db)):
    
    authenticated_user = login(user=user, db=db)

    if authenticated_user is None:
        raise HTTPException(status_code=401, detail="Email or Password is wrong")

    return {"message":"Login successfull"}

@app.put('/user-change/{username}', response_model=Profile)
def alter_user(username:str,user:Profile,db:Session = Depends(dep_db)):

    update_user = change_user(username=username,user=user,db=db)

    if(update_user is None):
        raise HTTPException(status_code=404, detail="User not Found")

    return update_user


@app.post('/create-post',response_model= Post)
def post(post:CreatePost, db:Session = Depends(dep_db)):
    try:
        created_post = create_post(post=post,db=db)

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