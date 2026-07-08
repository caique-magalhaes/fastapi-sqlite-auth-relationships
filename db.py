from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine


url = "sqlite:///./store-data.db"

engine = create_engine(url)


@event.listens_for(Engine, "connect")
def set_slite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autoflush=False, autocommit=False,bind=engine)

Base = declarative_base()