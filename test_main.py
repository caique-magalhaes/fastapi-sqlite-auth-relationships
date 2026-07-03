import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine,StaticPool
from sqlalchemy.orm import sessionmaker

# 1. Force Python to import your actual models right now
from db import Base
from main import app, dep_db

# 2. Setup our independent test database
SQLITE_DATABASE_URL = "sqlite://"

engine = create_engine(SQLITE_DATABASE_URL, connect_args={'check_same_thread': False},poolclass=StaticPool,)

TestingSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

@pytest.fixture(scope='function')
def db_session():
   
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='function')
def client(db_session):
    """Automates client creation and injects the database override."""

    def override_dep_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[dep_db] = override_dep_db
    yield TestClient(app)

    app.dependency_overrides.clear()
   


    



## ─── THE TESTS ────────────────────────────────────────────────────────

def test_read_root(client):
    """Test the basic landing endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_create_profile(client):
    """Test creating a brand new profile"""
    payload = {
        "name": "Anthony",
        "country": "Brazil",
        "city": "Sao Paulo"
    }
    response = client.post("/create-profile", json=payload)
    
    # Debugging print statement: if it fails, pytest will show us exactly what the server responded with!
    print("SERVER RESPONSE:", response.json()) 
    
    assert response.status_code == 200

def test_alter_user_not_found(client):
    payload={
        "name":"New Name",
        "country":"Brazil",
        "city":"Santos"
    }

    response = client.put("/user-change/ghost_user",json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not Found"