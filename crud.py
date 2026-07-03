from sqlalchemy.orm import Session
from profile import Profile
from models import User
from fastapi import HTTPException


def user_create(user:Profile, db:Session):
    table__user = User(name=user.name,country=user.country,city=user.city)
    
    db.add(table__user)
    db.commit()
    db.refresh(table__user)

    return table__user


def catch_user(db:Session, username:str):
    user = db.query(User).filter(User.name == username).first()
    if(user):
        return user
    else:
       raise HTTPException(status_code=404, detail="Usernot Found")


def change_user(db:Session, user:Profile,username:str):
    user_search = db.query(User).filter(User.name == username).first()
    
    if(user_search is None):
        return None

    user_search.name = user.name
    user_search.country = user.country
    user_search.city = user.city
    
    db.commit()
    db.refresh(user_search)

    return user_search

def delete_user(db:Session, username:str):
    user_search = db.query(User).filter(User.name == username).first()

    if(user_search is None):
        return None


    db.delete(user_search)
    db.commit()

    return user_search
        