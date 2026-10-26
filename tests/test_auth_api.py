"""Auth API integration on a disposable in-memory database, never the user's DB."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.auth import jwt

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(jwt,'SECRET_KEY','synthetic-test-secret-key-with-sufficient-length')
    engine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory=sessionmaker(bind=engine)
    def database():
        with factory() as session: yield session
    app.dependency_overrides[get_db]=database
    with TestClient(app) as client: yield client
    app.dependency_overrides.clear()
    engine.dispose()

def test_signup_login_and_me(client):
    payload={'email':'test@example.com','password':'SyntheticPass123','full_name':'Test Citizen'}
    assert client.post('/auth/signup',json=payload).status_code==201
    assert client.post('/auth/signup',json=payload).status_code==400
    response=client.post('/auth/login',json={'email':payload['email'],'password':payload['password']})
    assert response.status_code==200
    data=response.json()
    me=client.get('/auth/me',headers={'Authorization':'Bearer '+data['access_token']})
    assert me.status_code==200 and me.json()['email']==payload['email']
    assert 'hashed_password' not in me.json()
    assert client.post('/auth/login',json={'email':payload['email'],'password':'wrong'}).status_code==401

def test_signup_rejects_weak_or_overlong_password(client):
    for password in ('short','x'*73,'അ'*30):
        assert client.post('/auth/signup',json={'email':'test@example.com','password':password,'full_name':'Test'}).status_code==422
