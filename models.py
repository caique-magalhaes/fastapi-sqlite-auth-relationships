from sqlalchemy import String, Integer
from sqlalchemy.orm import mapped_column
from db import Base

class User(Base):
    __tablename__='user'
    id = mapped_column(Integer,primary_key=True)
    name = mapped_column(String(20))
    country = mapped_column(String(20))
    city = mapped_column(String(20))