from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


url = "sqlite:///./store-data.db"

engine = create_engine(url)
SessionLocal = sessionmaker(autoflush=False, autocommit=False,bind=engine)

Base = declarative_base()