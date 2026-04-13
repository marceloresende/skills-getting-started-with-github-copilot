import pytest


def test_root_redirect(client):
    """Test that root redirects to index.html"""
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    assert "Chess Club" in activities


def test_activity_structure(client):
    """Test that activities have the correct structure"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_details in activities.items():
        assert "description" in activity_details
        assert "schedule" in activity_details
        assert "max_participants" in activity_details
        assert "participants" in activity_details
        assert isinstance(activity_details["participants"], list)


def test_signup_for_activity(client):
    """Test signing up for an activity"""
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]


def test_signup_duplicate_email(client):
    """Test that duplicate signup is rejected"""
    email = "duplicate@mergington.edu"
    # First signup
    response1 = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response1.status_code == 200
    
    # Attempt duplicate signup
    response2 = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_nonexistent_activity(client):
    """Test signing up for non-existent activity"""
    response = client.post("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_remove_participant(client):
    """Test removing a participant"""
    email = "toremove@mergington.edu"
    activity = "Programming Class"
    
    # Add participant
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Verify participant was added
    response_before = client.get("/activities")
    assert email in response_before.json()[activity]["participants"]
    
    # Remove participant
    response = client.delete(f"/activities/{activity}/participants/{email}")
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]
    
    # Verify participant was removed
    response_after = client.get("/activities")
    assert email not in response_after.json()[activity]["participants"]


def test_remove_nonexistent_participant(client):
    """Test removing non-existent participant"""
    response = client.delete("/activities/Chess Club/participants/nonexistent@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_remove_from_nonexistent_activity(client):
    """Test removing from non-existent activity"""
    response = client.delete("/activities/Nonexistent Activity/participants/test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
