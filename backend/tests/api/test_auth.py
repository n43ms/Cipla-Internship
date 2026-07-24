from fastapi.testclient import TestClient
import pytest

from backend.app.main import app

client = TestClient(app)


def test_master_admin_login_success():
    response = client.post(
        "/api/auth/login",
        json={"email": "adityaxnema@gmail.com", "password": "Guddan@1205"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["email"] == "adityaxnema@gmail.com"
    assert data["isAdmin"] is True


def test_master_admin_login_invalid_password():
    response = client.post(
        "/api/auth/login",
        json={"email": "adityaxnema@gmail.com", "password": "WrongPassword123"},
    )
    assert response.status_code == 401
    assert "Incorrect password" in response.json()["detail"]


def test_cipla_user_login_success():
    response = client.post(
        "/api/auth/login",
        json={"email": "user.test@cipla.com", "password": "AdityaIntern@2026"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["email"] == "user.test@cipla.com"
    assert data["isAdmin"] is False


def test_whitelisted_admin_login_success():
    response = client.post(
        "/api/auth/login",
        json={"email": "abhijeet.mudila@cipla.com", "password": "AdityaIntern@2026"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["email"] == "abhijeet.mudila@cipla.com"
    assert data["isAdmin"] is True


def test_unauthorized_external_domain_rejected():
    response = client.post(
        "/api/auth/login",
        json={"email": "hacker@gmail.com", "password": "AdityaIntern@2026"},
    )
    assert response.status_code == 403
    assert "Email must end with @cipla.com" in response.json()["detail"]


def test_admin_change_password_success():
    # Admin changes password
    response = client.post(
        "/api/auth/change-password",
        json={
            "admin_email": "pralhad.gujar@cipla.com",
            "current_password": "AdityaIntern@2026",
            "new_password": "NewSecurePasscode2026!",
        },
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Cipla user logs in with new password
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "user.test@cipla.com", "password": "NewSecurePasscode2026!"},
    )
    assert login_resp.status_code == 200

    # Master admin password remains untouched ("Guddan@1205")
    master_login = client.post(
        "/api/auth/login",
        json={"email": "adityaxnema@gmail.com", "password": "Guddan@1205"},
    )
    assert master_login.status_code == 200

    # Reset password back to default for clean tests
    client.post(
        "/api/auth/change-password",
        json={
            "admin_email": "pralhad.gujar@cipla.com",
            "current_password": "NewSecurePasscode2026!",
            "new_password": "AdityaIntern@2026",
        },
    )


def test_non_admin_cannot_change_password():
    response = client.post(
        "/api/auth/change-password",
        json={
            "admin_email": "regular.user@cipla.com",
            "current_password": "AdityaIntern@2026",
            "new_password": "HackedPassword123",
        },
    )
    assert response.status_code == 403
    assert "Only designated administrators" in response.json()["detail"]
