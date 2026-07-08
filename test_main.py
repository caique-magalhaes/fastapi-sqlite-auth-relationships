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
        "city": "Sao Paulo",
        "email":"anthony@stark.com",
        "password":"Abc1234"
    }
    response = client.post("/create-profile", json=payload)
    
    # Debugging print statement: if it fails, pytest will show us exactly what the server responded with!
    print("SERVER RESPONSE:", response.json()) 
    
    assert response.status_code == 200


def test_create_profile_blank_field(client):
    payload_without_name = {
        "name":"",
        "country":"UK",
        "city":"London",
        "email":"george@test.com",
        "password":"Abc1234"
    }

    response = client.post("/create-profile", json=payload_without_name)

    assert response.status_code == 422

    payload_without_city = {
        "name":"George",
        "country":"UK",
        "city":"",
        "email":"george@test.com",
        "password":"Abc1234"
    }

    response = client.post("/create-profile", json=payload_without_city)

    assert response.status_code == 422

    payload_without_email = {
        "name":"George",
        "country":"UK",
        "city":"London",
        "email":"",
        "password":"Abc1234"
    }

    response = client.post("/create-profile", json=payload_without_email)

    assert response.status_code == 422

    payload_without_password = {
        "name":"George",
        "country":"UK",
        "city":"London",
        "email":"george@test.com",
        "password":""
    }

    response = client.post("/create-profile", json=payload_without_password)

    assert response.status_code == 422

    payload_without_country = {
        "name":"George",
        "country":"",
        "city":"London",
        "email":"george@test.com",
        "password":"Abc1234"
    }

    response = client.post('/create-profile', json = payload_without_country)

    assert response.json()['country'] == 'UK'

    assert response.status_code == 200



def test_create_profile_email_already_exist(client):
    payload = {
        "name": "Anthony",
        "country": "Brazil",
        "city": "Sao Paulo",
        "email":"anthony@stark.com",
        "password":"Abc1234"
    }
    client.post("/create-profile", json=payload)

    response = client.post("/create-profile",json=payload)

    assert response.status_code == 400


def test_create_post(client):
    user = {
        "name": "Pepper Potts",
        "country": "US",
        "city": "Malibu",
        "email": "pepper@stark.com",
        "password": "RescuePassword"
    }

    
    user_response = client.post("/create-profile",json=user)

    user_id = user_response.json()['id']

    payload = {
        "title":"Stark Industry",
        "description":"Come work for Starks Industries.",
        "user_id":user_id,

    }

    response = client.post("/create-post", json=payload)

    assert response.status_code == 200


def test_create_post_with_blank_field(client):
    user = {
    "name": "Pepper Potts",
    "country": "US",
    "city": "Malibu",
    "email": "pepper@stark.com",
    "password": "RescuePassword"
}   
    user_response = client.post("/create-profile",json=user)
    user_id = user_response.json()['id']

    post_without_title = {
        "title":"   ",
        "description":"Come work for Starks Industries.",
        "user_id":user_id,

    }

    response = client.post("/create-post", json=post_without_title)

    assert response.status_code == 422

    post_without_descritpion = {
        "title":"Stark Industry",
        "description":"  ",
        "user_id":user_id,
    }

    response = client.post("/create-post", json=post_without_descritpion)

    assert response.status_code == 422



def test_create_post_with_id_no_exist(client):
    
    post_user_id_not_exist = {
        "title":"Stark Industry",
        "description":"Come work for Starks Industries.",
        "user_id":2,
    }

    response = client.post("/create-post", json=post_user_id_not_exist)

    assert response.status_code == 422

    post_with_user_id_string = {
        "title":"Stark Industry",
        "description":"Come work for Starks Industries.",
        "user_id":"ok",
    }

    response = client.post("/create-post", json=post_with_user_id_string)

    assert response.status_code == 422
   
    
