from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, validates
from app.core.db import Base

class User(Base):
    __tablename__='users'
    id = mapped_column(Integer,primary_key=True)
    name = mapped_column(String(20))
    email = mapped_column(String(50), unique=True, index=True)
    country = mapped_column(String(20), default='UK')
    city = mapped_column(String(20))
    password = mapped_column(String(128))

    posts = relationship("Post", back_populates="user",cascade="all, delete-orphan") # When you delete the User record, SQLAlchemy automatically finds every single row in the posts table where the user_id matches that user, and issues a delete command for them too.
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")

    @validates('email','name','city','password','country')
    def empty_string_modifier(self, key, value):

        str_val = str(value).strip() if value is not None else ""

        if key == 'country' and not str_val:
            return 'BR'
        if not value or not str_val:
            raise ValueError(f"The field {key} cannot be blank or contain only whitespace.")
        return str_val


class Post(Base):
    __tablename__ = 'posts'

    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String(100))
    description = mapped_column(String(300))
    user_id = mapped_column(Integer, ForeignKey('users.id'), index=True)
    user = relationship("User",back_populates="posts")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")

    @validates('title','description')
    
    def empty_string_modifier(self, key, value):
        str_val = str(value).strip() if value is not None else ""
        if not value or not str_val:
            raise ValueError(f"The field {key} cannot be blank or contain only whitespace.")
        return str_val

class Like(Base):
    __tablename__ = 'likes'

    id_user = mapped_column(Integer, ForeignKey('users.id'),primary_key=True)
    id_post = mapped_column(Integer, ForeignKey('posts.id'), primary_key=True)
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")