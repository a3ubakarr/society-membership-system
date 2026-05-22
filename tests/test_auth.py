import pytest

def test_login_success(client):
    response = client.post("/", data={"username": "admin", "password": "admin123"})
    assert response.status_code == 302
    assert "/home" in response.headers["Location"]

def test_login_failure(client):
    response = client.post("/", data={"username": "wrong", "password": "wrong"})
    assert response.status_code == 200
    assert b"Login" in response.data

def test_login_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Login" in response.data
