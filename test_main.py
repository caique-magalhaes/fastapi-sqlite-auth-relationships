from typing import List

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
   


    

@pytest.fixture(scope='function')
def test_user_credentials():
    standard_user = {
        "name": "Anthony",
        "country": "Brazil",
        "city": "Sao Paulo",
        "email":"anthony@stark.com",
        "password":"Abc1234"
    }
    
    return standard_user


@pytest.fixture(scope='function')
def generate_token(client,test_user_credentials):
    response = client.post("/create-profile", json=test_user_credentials)

    user_info = {
        "username":test_user_credentials['email'],
        "password":test_user_credentials['password']
    }

    response = client.post('/user/login/token', data=user_info)
    json_data = response.json()
    
    return json_data.get('access_token')




## ─── THE TESTS ────────────────────────────────────────────────────────

def test_return_all_posts(client):
  
    response = client.get("/")
    
    assert response.status_code == 200
    assert isinstance(response.json(), List)

def test_create_profile(client,test_user_credentials):
    """Test creating a brand new profile"""
    
    response = client.post("/create-profile", json=test_user_credentials)
    
    # Debugging print statement: if it fails, pytest will show us exactly what the server responded with!
    print("SERVER RESPONSE:", response.json()) 
    
    assert response.status_code == 200


def test_login_for_access_token(client, test_user_credentials):
    """Check if it is returning the token in the response."""

    response = client.post("/create-profile", json=test_user_credentials)

    user_info = {
        "username":test_user_credentials['email'],
        "password":test_user_credentials['password']
    }

    response = client.post('/user/login/token', data=user_info)

    assert response.status_code == 200

    json_data = response.json()
    access_token = json_data.get('access_token')

    assert access_token is not None
    assert json_data.get('token_type') == "bearer"
    


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



def test_create_profile_email_already_exist(client, test_user_credentials):
    
    client.post("/create-profile", json=test_user_credentials)

    response = client.post("/create-profile",json=test_user_credentials)

    assert response.status_code == 400


def test_create_post_no_authenticated(client):
    payload = {
        "title":"Stark Industry",
        "description":"Come work for Starks Industries."
    }

    response = client.post("/create-post", json=payload)

    assert response.status_code == 401

def test_create_authenticated_post(client,generate_token):

    headers = {"Authorization": f"Bearer {generate_token}"}

    post = {
        "title":"Stark Industry",
        "description":"Come work for Starks Industries."
    }

    response = client.post("/create-post", json=post, headers=headers)

    assert response.status_code == 200

def test_create_post_with_blank_field(client, generate_token):

    headers = {"Authorization": f"Bearer {generate_token}"}

    post_without_title = {
        "title":"   ",
        "description":"Come work for Starks Industries.",
    }

    response = client.post("/create-post", json=post_without_title, headers=headers)

    assert response.status_code == 422

    post_without_descritpion = {
        "title":"Stark Industry",
        "description":"  ",
    }

    response = client.post("/create-post", json=post_without_descritpion,headers=headers)

    assert response.status_code == 422
   
    
def test_get_user_post(client, generate_token):    
    headers = {"Authorization": f"Bearer {generate_token}"}
    post = {
        "title":"Stark Industry",
        "description":"Come work for Starks Industries.",
    }
    
    repsonse_post = client.post("/create-post", json=post, headers=headers)
    
    user_id = repsonse_post.json()['user_id']
    response = client.get(f"/get-post/{user_id}")

    assert response.status_code == 200
    assert isinstance(response.json(), List)

def test_get_user_not_have_post(client):

    id_not_exist = 999

    response = client.get(f"/get-post/{id_not_exist}")

    assert response.status_code == 404
    assert response.json().get("detail") == "Post not found"
