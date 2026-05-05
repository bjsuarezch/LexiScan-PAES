import requests
import time
import pytest

BASE_URL = "http://127.0.0.1:8001"

def test_login_endpoint():
    """Test login endpoint responds in less than 5 seconds"""
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/login", json={
        "rut": "12345678-9",
        "password": "password123"
    })
    end_time = time.time()
    response_time = end_time - start_time

    assert response_time < 5, f"Login took {response_time} seconds, should be < 5"
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_dashboard_endpoint():
    """Test dashboard endpoint responds in less than 5 seconds"""
    # First login to get token
    login_response = requests.post(f"{BASE_URL}/login", json={
        "rut": "12345678-9",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    start_time = time.time()
    response = requests.get(f"{BASE_URL}/dashboard/12345678-9", headers=headers)
    end_time = time.time()
    response_time = end_time - start_time

    assert response_time < 5, f"Dashboard took {response_time} seconds, should be < 5"
    assert response.status_code == 200
    data = response.json()
    assert "usuario" in data
    assert "habilidades" in data
    assert "economia" in data

def test_habilidades_endpoint():
    """Test habilidades endpoint responds in less than 5 seconds"""
    # First login to get token
    login_response = requests.post(f"{BASE_URL}/login", json={
        "rut": "12345678-9",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    start_time = time.time()
    response = requests.get(f"{BASE_URL}/habilidades/Lectura Crítica", headers=headers)
    end_time = time.time()
    response_time = end_time - start_time

    assert response_time < 5, f"Habilidades took {response_time} seconds, should be < 5"
    assert response.status_code == 200
    data = response.json()
    assert "habilidad" in data
    assert "preguntas" in data
    assert len(data["preguntas"]) > 0