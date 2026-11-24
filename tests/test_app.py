import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def test_unregister_removes_participant(monkeypatch):
    activity_name = "Chess Club"
    email = "student@mergington.edu"
    monkeypatch.setitem(
        activities,
        activity_name,
        {**activities[activity_name], "participants": [email]},
    )

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

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
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == detail
