"""Tests for the project endpoints: create/list/get/delete/retry."""

from pathlib import Path

import pytest

from app.models import Output, OutputCategory, OutputStatus, OutputType, Project, ProjectStatus
from tests.conftest import auth_headers

API = "/api/v1/projects"
VALID_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture(autouse=True)
def _no_real_pipeline(monkeypatch):
    """Prevent the background pipeline from ever actually running in these tests."""
    monkeypatch.setattr("app.routers.projects.run_pipeline", lambda project_id: None)


def _create_project(client, access_token, source_url=VALID_URL, title="My Project"):
    return client.post(
        f"{API}/",
        json={"source_url": source_url, "title": title},
        headers=auth_headers(access_token),
    )


def _second_user_token(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "other@example.com", "password": "password123", "full_name": "Other"},
    )
    login = client.post(
        "/api/v1/auth/login",
        data={"username": "other@example.com", "password": "password123"},
    )
    return login.json()["access_token"]


class TestCreateProject:
    def test_create_success(self, client, test_user):
        _, access_token, _ = test_user
        response = _create_project(client, access_token)
        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "pending"
        assert body["source_url"] == VALID_URL
        assert body["title"] == "My Project"
        assert body["outputs"] == []

    def test_create_invalid_url(self, client, test_user):
        _, access_token, _ = test_user
        response = _create_project(client, access_token, source_url="not-a-url")
        assert response.status_code == 422

    def test_create_unauthenticated(self, client):
        response = client.post(f"{API}/", json={"source_url": VALID_URL})
        assert response.status_code == 401


class TestListProjects:
    def test_list_empty(self, client, test_user):
        _, access_token, _ = test_user
        response = client.get(f"{API}/", headers=auth_headers(access_token))
        assert response.status_code == 200
        assert response.json() == []

    def test_list_non_empty(self, client, test_user):
        _, access_token, _ = test_user
        _create_project(client, access_token, title="First")
        _create_project(client, access_token, title="Second")

        response = client.get(f"{API}/", headers=auth_headers(access_token))
        assert response.status_code == 200
        titles = {p["title"] for p in response.json()}
        assert titles == {"First", "Second"}

    def test_list_only_returns_own_projects(self, client, test_user):
        _, access_token, _ = test_user
        _create_project(client, access_token, title="Mine")

        other_token = _second_user_token(client)
        _create_project(client, other_token, title="Not Mine")

        response = client.get(f"{API}/", headers=auth_headers(access_token))
        titles = [p["title"] for p in response.json()]
        assert titles == ["Mine"]


class TestGetProject:
    def test_get_success(self, client, test_user):
        _, access_token, _ = test_user
        created = _create_project(client, access_token).json()

        response = client.get(f"{API}/{created['id']}", headers=auth_headers(access_token))
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_get_nonexistent(self, client, test_user):
        _, access_token, _ = test_user
        response = client.get(f"{API}/999999", headers=auth_headers(access_token))
        assert response.status_code == 404

    def test_get_someone_elses_project(self, client, test_user):
        _, access_token, _ = test_user
        created = _create_project(client, access_token).json()

        other_token = _second_user_token(client)
        response = client.get(f"{API}/{created['id']}", headers=auth_headers(other_token))
        assert response.status_code == 404


class TestDeleteProject:
    def test_delete_success(self, client, test_user):
        _, access_token, _ = test_user
        created = _create_project(client, access_token).json()

        response = client.delete(f"{API}/{created['id']}", headers=auth_headers(access_token))
        assert response.status_code == 204

        follow_up = client.get(f"{API}/{created['id']}", headers=auth_headers(access_token))
        assert follow_up.status_code == 404

    def test_delete_someone_elses_project(self, client, test_user):
        _, access_token, _ = test_user
        created = _create_project(client, access_token).json()

        other_token = _second_user_token(client)
        response = client.delete(f"{API}/{created['id']}", headers=auth_headers(other_token))
        assert response.status_code == 404

        # It's still there for the owner.
        still_there = client.get(f"{API}/{created['id']}", headers=auth_headers(access_token))
        assert still_there.status_code == 200


class TestRetryProject:
    def test_retry_conflict_when_not_failed(self, client, test_user):
        _, access_token, _ = test_user
        created = _create_project(client, access_token).json()
        assert created["status"] == "pending"

        response = client.post(f"{API}/{created['id']}/retry", headers=auth_headers(access_token))
        assert response.status_code == 409

    def test_retry_conflict_when_completed(self, client, test_user, db_session):
        _, access_token, _ = test_user
        created = _create_project(client, access_token).json()

        project = db_session.query(Project).filter(Project.id == created["id"]).first()
        project.status = ProjectStatus.completed
        db_session.add(project)
        db_session.commit()

        response = client.post(f"{API}/{created['id']}/retry", headers=auth_headers(access_token))
        assert response.status_code == 409

    def test_retry_success_when_failed(self, client, test_user, db_session):
        _, access_token, _ = test_user
        created = _create_project(client, access_token).json()

        project = db_session.query(Project).filter(Project.id == created["id"]).first()
        project.status = ProjectStatus.failed
        project.error_message = "boom"
        db_session.add(project)
        db_session.commit()

        response = client.post(f"{API}/{created['id']}/retry", headers=auth_headers(access_token))
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "pending"
        assert body["error_message"] is None


class TestDownloadOutput:
    def _make_output(self, db_session, project_id, tmp_path, status=OutputStatus.completed, with_file=True):
        file_path = None
        if with_file:
            file_path = tmp_path / "trailer_30s.mp4"
            file_path.write_bytes(b"fake rendered video")

        output = Output(
            project_id=project_id,
            output_type=OutputType.trailer_30s,
            category=OutputCategory.energetic,
            status=status,
            file_path=str(file_path) if file_path else None,
            duration_seconds=30.0 if status == OutputStatus.completed else None,
        )
        db_session.add(output)
        db_session.commit()
        db_session.refresh(output)
        return output

    def test_download_success(self, client, test_user, db_session, tmp_path):
        _, access_token, _ = test_user
        created = _create_project(client, access_token).json()
        output = self._make_output(db_session, created["id"], tmp_path)

        response = client.get(
            f"{API}/{created['id']}/outputs/{output.id}/download",
            headers=auth_headers(access_token),
        )
        assert response.status_code == 200
        assert response.content == b"fake rendered video"

    def test_download_not_completed_returns_404(self, client, test_user, db_session, tmp_path):
        _, access_token, _ = test_user
        created = _create_project(client, access_token).json()
        output = self._make_output(db_session, created["id"], tmp_path, status=OutputStatus.rendering)

        response = client.get(
            f"{API}/{created['id']}/outputs/{output.id}/download",
            headers=auth_headers(access_token),
        )
        assert response.status_code == 404

    def test_download_missing_file_returns_404(self, client, test_user, db_session, tmp_path):
        _, access_token, _ = test_user
        created = _create_project(client, access_token).json()
        output = self._make_output(db_session, created["id"], tmp_path)
        # Remove the file after creating the (completed) Output row referencing it.
        Path(output.file_path).unlink()

        response = client.get(
            f"{API}/{created['id']}/outputs/{output.id}/download",
            headers=auth_headers(access_token),
        )
        assert response.status_code == 404

    def test_download_nonexistent_output_returns_404(self, client, test_user):
        _, access_token, _ = test_user
        created = _create_project(client, access_token).json()

        response = client.get(
            f"{API}/{created['id']}/outputs/999999/download",
            headers=auth_headers(access_token),
        )
        assert response.status_code == 404
