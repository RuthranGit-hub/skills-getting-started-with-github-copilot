from urllib.parse import quote
from uuid import uuid4

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def build_activity_url(activity_name: str, action: str, email: str = None) -> str:
    url = f"/activities/{quote(activity_name)}/{action}"
    if email:
        url = f"{url}?email={quote(email)}"
    return url


def signup_participant(activity_name: str, email: str):
    return client.post(build_activity_url(activity_name, "signup", email))


def remove_participant(activity_name: str, email: str):
    return client.delete(build_activity_url(activity_name, "participants", email))


def get_activities():
    return client.get("/activities")


def test_root_redirects():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_dict():
    # Act
    response = get_activities()

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload


def test_signup_and_duplicate_signup():
    # Arrange
    activity_name = "Chess Club"
    email = f"tester-{uuid4().hex}@mergington.edu"

    # Act
    signup_response = signup_participant(activity_name, email)

    # Assert
    assert signup_response.status_code == 200
    assert signup_response.json()["message"] == f"Signed up {email} for {activity_name}"

    # Act
    duplicate_response = signup_participant(activity_name, email)

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant():
    # Arrange
    activity_name = "Programming Class"
    email = f"remove-{uuid4().hex}@mergington.edu"

    signup_response = signup_participant(activity_name, email)
    assert signup_response.status_code == 200

    # Act
    delete_response = remove_participant(activity_name, email)

    # Assert
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Removed {email} from {activity_name}"

    # Act
    activities_response = get_activities()

    # Assert
    assert email not in activities_response.json()[activity_name]["participants"]

    # Act
    missing_response = remove_participant(activity_name, email)

    # Assert
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Participant not found"
