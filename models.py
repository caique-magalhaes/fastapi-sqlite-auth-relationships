from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, validates
from db import Base

class User(Base):
    __tablename__='user'
    id = mapped_column(Integer,primary_key=True)
    name = mapped_column(String(20))
    email = mapped_column(String(50), unique=True, index=True)
    country = mapped_column(String(20), default='UK')
    city = mapped_column(String(20))
    password = mapped_column(String(128))

    posts = relationship("Post", back_populates="user",cascade="all, delete-orphan") # When you delete the User record, SQLAlchemy automatically finds every single row in the posts table where the user_id matches that user, and issues a delete command for them too.

    @validates('email','name','city','password','country')
    def empty_string_modifier(self, key, value):
        if key == 'country' and not value.strip():
            value = 'UK'
        if not value or not value.strip():
            raise ValueError(f"The field {key} cannot be blank or contain only whitespace.")
        return value.strip()
    


class Post(Base):
    __tablename__ = 'posts'

    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String(100))
    description = mapped_column(String(300))
    user_id = mapped_column(Integer, ForeignKey('user.id'), index=True)
    user = relationship("User",back_populates="posts")

    @validates('title','description')
    def empty_string_modifier(self, key, value):
        if not value or not value.strip():
            raise ValueError(f"The field {key} cannot be blank or contain only whitespace.")
        return value.strip()