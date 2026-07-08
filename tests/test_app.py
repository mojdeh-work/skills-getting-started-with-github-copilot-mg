import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = copy.deepcopy(app_module.activities)
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_state))
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_state))


@pytest.fixture
def client():
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_available_activities(client):
    endpoint = "/activities"

    response = client.get(endpoint)

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_adds_participant(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_for_activity_rejects_duplicate_signups(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    duplicate_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_existing_student(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_participant_returns_not_found_for_unknown_student(client):
    activity_name = "Chess Club"
    email = "unknown@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
