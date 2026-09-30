import pytest

from app import create_app
from app.models import Project, Task


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "APP_PASSWORD": None,
        }
    )
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_index_empty(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"No projects yet" in resp.data


def test_create_project_and_task_flow(app, client):
    resp = client.post(
        "/projects", data={"name": "Circuit board v2"}, follow_redirects=True
    )
    assert b"Circuit board v2" in resp.data

    with app.app_context():
        project = Project.query.first()
        assert project is not None
        pid = project.id

    resp = client.post(
        f"/projects/{pid}/tasks", data={"text": "Solder headers"}, follow_redirects=True
    )
    assert b"Solder headers" in resp.data
    assert b"0/1" in resp.data

    with app.app_context():
        task = Task.query.first()
        tid = task.id

    resp = client.post(f"/tasks/{tid}/toggle", follow_redirects=True)
    assert b"1/1" in resp.data

    resp = client.post(f"/tasks/{tid}/delete", follow_redirects=True)
    assert b"Solder headers" not in resp.data

    resp = client.post(f"/projects/{pid}/delete", follow_redirects=True)
    assert b"Circuit board v2" not in resp.data
    assert b"No projects yet" in resp.data


def test_login_gate(app, client):
    app.config["APP_PASSWORD"] = "secret123"

    resp = client.get("/", follow_redirects=True)
    assert b"Password" in resp.data

    resp = client.post("/login", data={"password": "wrong"})
    assert b"Wrong password" in resp.data

    resp = client.post(
        "/login", data={"password": "secret123"}, follow_redirects=True
    )
    assert b"No projects yet" in resp.data
