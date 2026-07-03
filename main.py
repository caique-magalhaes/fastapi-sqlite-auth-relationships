from fastapi import FastAPI,Depends,HTTPException
from profile import Profile
from sqlalchemy.orm import Session
from crud import user_create, catch_user, change_user, delete_user
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

@app.post('/create-profile')
def create_profile(user:Profile,db:Session = Depends(dep_db)):
    
    return user_create(user=user,db=db)

@app.get('/user/{username}',response_model=Profile)
def get_user(username:str,db:Session = Depends(dep_db)):
    
    return catch_user(username=username, db=db)

@app.put('/user-change/{username}', response_model=Profile)
def alter_user(username:str,user:Profile,db:Session = Depends(dep_db)):

    update_user = change_user(username=username,user=user,db=db)

    if(update_user is None):
        raise HTTPException(status_code=404, detail="User not Found")

    return update_user

@app.delete('/user-delete/{username}')
def delete(username:str,db:Session = Depends(dep_db)):

    deleted_user = delete_user(username=username,db=db)

    if(deleted_user is None):
        raise HTTPException(status_code=404, detail="User not Found")

    return {"successful":"User has been Deleted"}