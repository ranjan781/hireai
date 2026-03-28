import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

def test_health_check():
    """Server chal raha hai?"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_register_hr():
    """HR register kar sakta hai?"""
    response = client.post("/api/v1/auth/register", json={
        "email": "test_hr_unique@test.com",
        "full_name": "Test HR",
        "password": "Test@1234",
        "role": "hr",
        "company": "Test Company"
    })
    assert response.status_code in [201, 400]  # 400 = already exists
    if response.status_code == 201:
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "hr"

def test_register_applicant():
    """Applicant register kar sakta hai?"""
    response = client.post("/api/v1/auth/register", json={
        "email": "test_applicant_unique@test.com",
        "full_name": "Test Applicant",
        "password": "Test@1234",
        "role": "applicant"
    })
    assert response.status_code in [201, 400]

def test_login_success():
    """Valid credentials se login hoga?"""
    # Pehle register karo
    client.post("/api/v1/auth/register", json={
        "email": "login_test@test.com",
        "full_name": "Login Test",
        "password": "Test@1234",
        "role": "applicant"
    })
    # Phir login karo
    response = client.post("/api/v1/auth/login", json={
        "email": "login_test@test.com",
        "password": "Test@1234"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_login_wrong_password():
    """Galat password reject hoga?"""
    response = client.post("/api/v1/auth/login", json={
        "email": "priya@techcorp.com",
        "password": "WrongPassword123"
    })
    assert response.status_code == 401

def test_login_nonexistent_user():
    """Nonexistent user reject hoga?"""
    response = client.post("/api/v1/auth/login", json={
        "email": "nobody@nowhere.com",
        "password": "Test@1234"
    })
    assert response.status_code == 401

def test_protected_route_without_token():
    """Token ke bina protected route block hoga?"""
    response = client.get("/api/v1/jobs")
    assert response.status_code == 403

def test_jobs_list_with_token():
    """Valid token se jobs dekh sakte hain?"""
    # Login karo
    login = client.post("/api/v1/auth/login", json={
        "email": "login_test@test.com",
        "password": "Test@1234"
    })
    token = login.json()["access_token"]
    
    response = client.get(
        "/api/v1/jobs",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_short_password_rejected():
    """Chota password reject hoga?"""
    response = client.post("/api/v1/auth/register", json={
        "email": "shortpass@test.com",
        "full_name": "Short Pass",
        "password": "abc",
        "role": "applicant"
    })
    assert response.status_code == 422

def test_invalid_email_rejected():
    """Invalid email reject hoga?"""
    response = client.post("/api/v1/auth/register", json={
        "email": "not-an-email",
        "full_name": "Bad Email",
        "password": "Test@1234",
        "role": "applicant"
    })
    assert response.status_code == 422

def test_security_headers():
    """Security headers hain?"""
    response = client.get("/health")
    assert "x-content-type-options" in response.headers
    assert "x-frame-options" in response.headers