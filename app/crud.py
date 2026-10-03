from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.profile import UserLogin, UserCreate, CreatePost
from app.models import User, Post, Like
from app.core.authenticated import get_hash, check_password


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

def user_me(email:str, db:Session):
    user = db.query(User).filter(User.email == email).first()
    return user

def login(db:Session, user:UserLogin):
    get_user = db.query(User).filter(User.email == user.email).first()
    if get_user is None:
        return None
    is_hash_valid = check_password(hashed=get_user.password,password=user.password)
    if(is_hash_valid):
        return get_user
    return None


def change_post(post_id:int ,new_post:CreatePost, email:str,db:Session):
    user_search = db.query(User).filter(User.email == email).first()
    upload_post = db.query(Post).filter(Post.id == post_id).first()

    if user_search is None:
        return "forbidden"
    if upload_post is None:
        return None
    if user_search.id != upload_post.user_id:
        return "forbidden"
    upload_post.title = new_post.title
    upload_post.description = new_post.description
    try:
        db.commit()
        db.refresh(upload_post)
        return upload_post
    except IntegrityError:
        db.rollback()

        return None

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

def delete_post(db:Session, post_id:int, email:str):
    user_search = db.query(User).filter(User.email == email).first()
    post_search = db.query(Post).filter(Post.id == post_id).first()
    if user_search is None:
        return "forbidden"
    if post_search is None:
        return None
    if post_search.user_id != user_search.id:
        return "forbidden"
    try:
        db.delete(post_search)
        db.commit()
        return post_search
    except IntegrityError:
        db.rollback()
        return None

def give_or_remove_like(db:Session, post_id:int, email:str):
    user = db.query(User).filter(User.email == email).first()
    post = db.query(Post).filter(Post.id == post_id).first()
    if user is None:
        return 'forbidden'

    if post is None:
        return 'not found'
    like_search = db.query(Like).filter(Like.id_post == post.id, Like.id_user == user.id).first()

    if like_search is not None:
        db.delete(like_search)
        db.commit()
        return {'action':'unlike', 'like':like_search}
    created_like = Like(id_user = user.id, id_post = post_id)
    try:
        db.add(created_like)
        db.commit()
        db.refresh(created_like)
        return {'action':'like', 'like':created_like}
    except IntegrityError:
        db.rollback()
        return None