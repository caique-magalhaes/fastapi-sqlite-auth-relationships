import os 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = os.getenv("DATABASE_URL","sqlite://")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False,bind=engine)

Base = declarative_base()

#dependency
def dep_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()