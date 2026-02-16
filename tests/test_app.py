import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure src is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app import app, activities  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)


def test_root_redirect(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Basketball" in data


def test_signup_and_unregister_cycle(client):
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure clean state: remove if present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # Duplicate signup should fail
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400

    # Unregister
    resp3 = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp3.status_code == 200
    assert email not in activities[activity]["participants"]


def test_signup_nonexistent_activity(client):
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "x@x.com"})
    assert resp.status_code == 404


def test_unregister_nonparticipant(client):
    activity = "Robotics Club"
    email = "notregistered@example.com"
    # Ensure not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 404
