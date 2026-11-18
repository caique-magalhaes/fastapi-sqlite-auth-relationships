from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import mapped_column, relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.db import Base

class User(Base):
    __tablename__='users'
    id = mapped_column(Integer,primary_key=True)
    name = mapped_column(String(20), nullable=False)
    email = mapped_column(String(50), unique=True, index=True, nullable=False)
    email_confirmed = mapped_column(Boolean, default=False)
    country = mapped_column(String(20), default='Brazil')
    password = mapped_column(String(128), nullable=False)
    username = mapped_column(String(30), unique=True, index=True, nullable=False)

    posts = relationship("Post", back_populates="user",cascade="all, delete-orphan", foreign_keys="Post.user_id") # When you delete the User record, SQLAlchemy automatically finds every single row in the posts table where the user_id matches that user, and issues a delete command for them too.
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")

    @hybrid_property
    def like_post_ids(self):
        return [like.id_post for like in getattr(self, 'likes', [])]

    @validates('email','name','city','password','country','username')
    def empty_string_modifier(self, key, value):

        str_val = str(value).strip() if value is not None else ""

        if key == 'country' and not str_val:
            return 'Brazil'
        if not value or not str_val:
            raise ValueError(f"The field {key} cannot be blank or contain only whitespace.")
        return str_val


class Post(Base):
    __tablename__ = 'posts'

    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String(100), nullable=False)
    description = mapped_column(String(300), nullable=False)
    user_id = mapped_column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    user_name = mapped_column(String, ForeignKey('users.username'), index=True, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default= func.now(), nullable=False)
    user = relationship("User",back_populates="posts", foreign_keys='Post.user_id')
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")

    @hybrid_property
    def like_count(self):
        return len((self.likes)) if self.likes else 0

    @validates('title','description')
    def empty_string_modifier(self, key, value):
        str_val = str(value).strip() if value is not None else ""
        if not value or not str_val:
            raise ValueError(f"The field {key} cannot be blank or contain only whitespace.")
        return str_val

class Like(Base):
    __tablename__ = 'likes'

    id_user = mapped_column(Integer, ForeignKey('users.id'),primary_key=True, nullable=False)
    id_post = mapped_column(Integer, ForeignKey('posts.id'), primary_key=True, nullable=False)
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")