from dotenv import dotenv_values
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine

configure_env = dotenv_values(".env")

DATABASE_URL = configure_env.get("DATABASE_URL")

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