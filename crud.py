from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from profile import Profile, UserLogin, UserCreate, CreatePost
from models import User, Post
from authenticated import get_hash, check_password


def return_all_posts(db:Session):
    
    posts = db.query(Post).all()

    return posts

def get_user_post(user_id:int, db:Session):
    posts = db.query(Post).filter(Post.user_id == user_id).all()

    if not posts:
        return None
    return posts

def user_create(user:UserCreate, db:Session):
    hash_password = get_hash(user.password)
    
    table__user = User(name=user.name,country=user.country,city=user.city,email=user.email,password=hash_password)

    try:

        db.add(table__user)
        db.commit()
        db.refresh(table__user)

        return table__user

    except IntegrityError:
        db.rollback()

        return None


def login(db:Session, user:UserLogin):
    get_user = db.query(User).filter(User.email == user.email).first()
    

    if get_user is None:
        return None
    is_hash_valid = check_password(hashed=get_user.password,password=user.password)
    
    if(is_hash_valid):
        return get_user
    
    return None


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


def create_post(post:CreatePost, db:Session, user_id:int):
    created_post = Post(title = post.title, description = post.description, user_id = user_id)

    try:
        db.add(created_post)
        db.commit()
        db.refresh(created_post)

        return created_post

    except IntegrityError:
        db.rollback()

        return None

def delete_user(db:Session, username:str):
    user_search = db.query(User).filter(User.name == username).first()

    if(user_search is None):
        return None


    db.delete(user_search)
    db.commit()

    return user_search
        