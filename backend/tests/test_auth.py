"""Tests for the auth module: register, login, /me, refresh, logout."""

from datetime import UTC, datetime, timedelta

from app.models import RefreshToken
from tests.conftest import auth_headers

API = "/api/v1/auth"


def _register(client, email="new@example.com", password="password123", full_name="New User"):
    return client.post(
        f"{API}/register",
        json={"email": email, "password": password, "full_name": full_name},
    )


def _login(client, email="new@example.com", password="password123"):
    return client.post(f"{API}/login", data={"username": email, "password": password})


class TestRegister:
    def test_register_success(self, client):
        response = _register(client)
        assert response.status_code == 201
        body = response.json()
        assert body["email"] == "new@example.com"
        assert body["full_name"] == "New User"
        assert body["is_active"] is True
        assert body["is_verified"] is False
        assert "id" in body
        assert "hashed_password" not in body

    def test_register_duplicate_email_conflicts(self, client):
        first = _register(client)
        assert first.status_code == 201

        second = _register(client)
        assert second.status_code == 409
        assert second.json()["code"] == "CONFLICT"

    def test_register_password_too_short_is_rejected(self, client):
        response = _register(client, password="short")
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client):
        _register(client)
        response = _login(client)
        assert response.status_code == 200
        body = response.json()
        assert body["token_type"] == "bearer"
        assert body["access_token"]
        assert body["refresh_token"]

    def test_login_wrong_password(self, client):
        _register(client)
        response = _login(client, password="wrong-password")
        assert response.status_code == 401

    def test_login_unknown_email(self, client):
        response = _login(client, email="ghost@example.com")
        assert response.status_code == 401


class TestMe:
    def test_get_me_success(self, client, test_user):
        _, access_token, _ = test_user
        response = client.get(f"{API}/me", headers=auth_headers(access_token))
        assert response.status_code == 200
        assert response.json()["email"] == "user@example.com"

    def test_get_me_missing_token(self, client):
        response = client.get(f"{API}/me")
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        response = client.get(f"{API}/me", headers=auth_headers("not-a-real-token"))
        assert response.status_code == 401

    def test_update_me(self, client, test_user):
        _, access_token, _ = test_user
        response = client.put(
            f"{API}/me",
            json={"full_name": "Updated Name"},
            headers=auth_headers(access_token),
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Name"

        # Persisted: a subsequent GET reflects the change.
        follow_up = client.get(f"{API}/me", headers=auth_headers(access_token))
        assert follow_up.json()["full_name"] == "Updated Name"


class TestRefresh:
    def test_refresh_success_and_rotation(self, client, test_user):
        _, _, refresh_token = test_user

        response = client.post(f"{API}/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 200
        body = response.json()
        new_refresh_token = body["refresh_token"]
        assert new_refresh_token != refresh_token
        assert body["access_token"]

        # The OLD refresh token must no longer work after rotation.
        old_reuse = client.post(f"{API}/refresh", json={"refresh_token": refresh_token})
        assert old_reuse.status_code == 401

        # The NEW refresh token does work.
        second = client.post(f"{API}/refresh", json={"refresh_token": new_refresh_token})
        assert second.status_code == 200

    def test_refresh_unknown_token(self, client):
        response = client.post(f"{API}/refresh", json={"refresh_token": "does-not-exist"})
        assert response.status_code == 401

    def test_refresh_revoked_token(self, client, test_user, db_session):
        _, _, refresh_token = test_user
        stored = db_session.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
        stored.revoked = True
        db_session.add(stored)
        db_session.commit()

        response = client.post(f"{API}/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 401

    def test_refresh_expired_token(self, client, test_user, db_session):
        _, _, refresh_token = test_user
        stored = db_session.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
        stored.expires_at = datetime.now(UTC) - timedelta(days=1)
        db_session.add(stored)
        db_session.commit()

        response = client.post(f"{API}/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 401


class TestLogout:
    def test_logout_revokes_token(self, client, test_user):
        _, _, refresh_token = test_user

        response = client.post(f"{API}/logout", json={"refresh_token": refresh_token})
        assert response.status_code == 204

        follow_up = client.post(f"{API}/refresh", json={"refresh_token": refresh_token})
        assert follow_up.status_code == 401

    def test_logout_unknown_token_is_a_noop(self, client):
        response = client.post(f"{API}/logout", json={"refresh_token": "does-not-exist"})
        assert response.status_code == 204
