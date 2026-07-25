from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.profile import Post, CreatePost
from sqlalchemy.orm import Session
from app.core.authenticated import get_current_user
from app.crud import get_user_post, change_post, create_post, delete_post
from app.core.db  import dep_db
from app.models import User

router = APIRouter(
    prefix="/post",
    tags=["Posts"]
    )

@router.post('/create-post',response_model=Post)
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



@router.get('/get-post/{user_id}', response_model=List[Post])
def user_post(user_id:int, db:Session = Depends(dep_db)):

    user_post = get_user_post(user_id=user_id, db=db)

    if user_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return user_post
   




@router.put('/post-change/{post_id}', response_model=Post)
def alter_post(post_id:int, new_post:CreatePost ,db:Session = Depends(dep_db),current_user: str = Depends(get_current_user)):

    update_post = change_post(post_id=post_id, new_post=new_post,email=current_user, db=db)

    if(update_post is None):
        raise HTTPException(status_code=404, detail="Post not Found")
    
    if update_post == "forbidden":
        raise HTTPException(status_code=403,detail="You are not authorized to update this post", headers={"WWW-Authenticate": "Bearer"})

    return update_post

    
@router.delete('/post-delete/{post_id}')
def delete(post_id:int, db:Session = Depends(dep_db), current_user: str = Depends(get_current_user)):
    
    post = delete_post(db=db, post_id=post_id, email=current_user)

    if(post is None):
        raise HTTPException(status_code=404, detail="Post not Found")
    
    if(post == "forbidden"):
        raise HTTPException(status_code=403,detail="You are not authorized to delete this post", headers={"WWW-Authenticate": "Bearer"})

    return {"successful":"Post has been Deleted", "post":post}


