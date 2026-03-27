"""
Tests for the GET /activities endpoint.

Verifies:
- All activities are returned
- Response has correct structure
- Each activity has required fields
- Available_spots calculation is correct
"""

import pytest


def test_get_all_activities_returns_list(client):
    """
    ARRANGE: Fresh client with initialized activities
    ACT: GET /activities
    ASSERT: Returns list with all 9 activities
    """
    # ARRANGE: client fixture provides fresh app state
    
    # ACT: Get all activities
    response = client.get("/activities")
    
    # ASSERT: Check response
    assert response.status_code == 200
    activities = response.json()
    assert len(activities) == 9
    assert isinstance(activities, list)


def test_activities_have_required_fields(client):
    """
    ARRANGE: Fresh client with initialized activities
    ACT: GET /activities
    ASSERT: Each activity has required fields
    """
    # ARRANGE: client fixture provides fresh app state
    required_fields = {"name", "description", "schedule", "max_participants", "participants", "available_spots"}
    
    # ACT: Get all activities
    response = client.get("/activities")
    activities = response.json()
    
    # ASSERT: Check each activity has all required fields
    for activity in activities:
        assert set(activity.keys()) == required_fields, f"Activity {activity.get('name')} missing fields"
        assert isinstance(activity["participants"], list)
        assert isinstance(activity["max_participants"], int)
        assert isinstance(activity["available_spots"], int)


def test_available_spots_calculated_correctly(client):
    """
    ARRANGE: Fresh client with activities (Chess Club has 12 max, 2 participants)
    ACT: GET /activities
    ASSERT: available_spots = max_participants - len(participants)
    """
    # ARRANGE: client fixture provides fresh app state
    
    # ACT: Get all activities
    response = client.get("/activities")
    activities = response.json()
    
    # ASSERT: Verify available_spots calculation for Chess Club
    chess_club = next(a for a in activities if a["name"] == "Chess Club")
    expected_available = chess_club["max_participants"] - len(chess_club["participants"])
    assert chess_club["available_spots"] == expected_available
    assert chess_club["available_spots"] == 10  # 12 - 2


def test_activities_contain_initial_participants(client):
    """
    ARRANGE: Fresh client with initialized activities
    ACT: GET /activities
    ASSERT: Initial participants are present
    """
    # ARRANGE: client fixture provides fresh app state
    
    # ACT: Get all activities
    response = client.get("/activities")
    activities = response.json()
    
    # ASSERT: Check that Chess Club contains initial participants
    chess_club = next(a for a in activities if a["name"] == "Chess Club")
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


def test_get_activities_returns_all_nine_activities(client):
    """
    ARRANGE: Fresh client with initialized activities
    ACT: GET /activities
    ASSERT: All 9 activities are returned with correct names
    """
    # ARRANGE: client fixture provides fresh app state
    expected_activity_names = {
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Tennis Club",
        "Art Studio",
        "Music Ensemble",
        "Debate Team",
        "Science Club"
    }
    
    # ACT: Get all activities
    response = client.get("/activities")
    activities = response.json()
    
    # ASSERT: Verify all activities are present
    actual_names = {activity["name"] for activity in activities}
    assert actual_names == expected_activity_names
