from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_root_redirects_to_static_app():
    # Arrange
    # The app and client are configured at module level.

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data():
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert activity_name in response.json()
    assert response.json()[activity_name] == activities[activity_name]


def test_signup_adds_participant(monkeypatch):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    monkeypatch.setitem(
        activities,
        activity_name,
        {**activities[activity_name], "participants": []},
    )

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in activities[activity_name]["participants"]


def test_signup_reports_unknown_activity():
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(monkeypatch):
    # Arrange
    activity_name = "Chess Club"
    email = "student@mergington.edu"
    monkeypatch.setitem(
        activities,
        activity_name,
        {**activities[activity_name], "participants": [email]},
    )

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in activities[activity_name]["participants"]


@pytest.mark.parametrize(
    ("activity_name", "email", "detail"),
    [
        ("Unknown Activity", "student@mergington.edu", "Activity not found"),
        ("Chess Club", "missing@mergington.edu", "Participant not found"),
    ],
)
def test_unregister_reports_missing_activity_or_participant(
    activity_name, email, detail
):
    # Arrange
    # The missing activity and participant cases are supplied by parametrization.

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == detail
