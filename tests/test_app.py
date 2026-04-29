from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_activities_returns_available_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "test_signup_user@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/signup"
    params = {"email": email}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activity_response = client.get("/activities")
    assert email in activity_response.json()[activity_name]["participants"]


def test_signup_duplicate_participant_returns_bad_request():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/signup"
    params = {"email": email}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_successfully_unregisters_participant():
    # Arrange
    activity_name = "Programming Class"
    email = "delete_test_user@mergington.edu"
    signup_url = f"/activities/{quote(activity_name, safe='')}/signup"
    params = {"email": email}

    signup_response = client.post(signup_url, params=params)
    assert signup_response.status_code == 200

    delete_url = f"/activities/{quote(activity_name, safe='')}/participants"

    # Act
    response = client.delete(delete_url, params=params)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    activity_response = client.get("/activities")
    assert email not in activity_response.json()[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_not_found():
    # Arrange
    activity_name = "Art Club"
    email = "missing_user@mergington.edu"
    delete_url = f"/activities/{quote(activity_name, safe='')}/participants"
    params = {"email": email}

    # Act
    response = client.delete(delete_url, params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
