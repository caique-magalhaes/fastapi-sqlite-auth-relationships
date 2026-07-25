from fastapi import APIRouter, Depends, HTTPException,Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.db  import dep_db
from app.core.authenticated import create_access_token
from app.crud import user_create, login
from app.profile import UserLogin, UserCreate, Profile
from datetime import timedelta


ACCESS_TOKEN_EXPIRE_MINUTES = 30
router = APIRouter(
    prefix="/user",
    tags=["Users"]               )

@router.post('/register', response_model=Profile)
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


@router.post('/login/token')
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

@router.post('/logout')
def logout(response:Response):
    response.delete_cookie(key="access_token", path="/", httponly=True)

    return{"message":"Successfully logged out!!"}

