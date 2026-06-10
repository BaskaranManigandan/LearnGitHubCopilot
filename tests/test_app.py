from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
ORIGINAL_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = deepcopy(ORIGINAL_ACTIVITIES)
    yield


def test_get_activities_returns_known_activities():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    # Arrange
    email = "teststudent@mergington.edu"
    encoded_activity = quote("Chess Club")
    url = f"/activities/{encoded_activity}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    email = "michael@mergington.edu"
    encoded_activity = quote("Chess Club")
    url = f"/activities/{encoded_activity}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant():
    # Arrange
    email = "daniel@mergington.edu"
    encoded_activity = quote("Chess Club")
    encoded_email = quote(email)
    url = f"/activities/{encoded_activity}/participants/{encoded_email}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    email = "missing@mergington.edu"
    encoded_activity = quote("Chess Club")
    encoded_email = quote(email)
    url = f"/activities/{encoded_activity}/participants/{encoded_email}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
