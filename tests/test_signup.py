"""
Tests for the POST /activities/{activity_name}/signup endpoint.

Verifies:
- Successful signup with valid email
- Activity not found error (404)
- Student already signed up error (400)
- Invalid email format error (422)
- Capacity full error (400)
- Email is added to participants list
"""

import pytest


def test_signup_success_with_valid_email(client, valid_email):
    """
    ARRANGE: Fresh client, valid email not yet signed up, activity exists
    ACT: POST /activities/Chess Club/signup?email=...
    ASSERT: Returns 200, email added to participants
    """
    # ARRANGE: client fixture provides fresh app state, valid_email provided
    
    # ACT: Sign up for activity
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": valid_email}
    )
    
    # ASSERT: Check response and participant list
    assert response.status_code == 200
    assert response.json()["email"] == valid_email
    assert response.json()["activity"] == "Chess Club"
    
    # Verify email was added to participants
    activities_response = client.get("/activities")
    chess_club = next(a for a in activities_response.json() if a["name"] == "Chess Club")
    assert valid_email in chess_club["participants"]


def test_signup_fails_activity_not_found(client, valid_email, nonexistent_activity):
    """
    ARRANGE: Fresh client, valid email, activity does not exist
    ACT: POST /activities/Nonexistent Activity/signup?email=...
    ASSERT: Returns 404, 'Activity not found'
    """
    # ARRANGE: client fixture provides fresh app state, nonexistent_activity provided
    
    # ACT: Sign up for non-existent activity
    response = client.post(
        f"/activities/{nonexistent_activity}/signup",
        params={"email": valid_email}
    )
    
    # ASSERT: Check error response
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_fails_already_signed_up(client, activity_name, already_signed_up_email):
    """
    ARRANGE: Fresh client, email already enrolled in activity
    ACT: POST /activities/Chess Club/signup?email=michael@mergington.edu
    ASSERT: Returns 400, 'already signed up'
    """
    # ARRANGE: client fixture provides fresh app state
    # already_signed_up_email (michael@mergington.edu) is already in Chess Club
    
    # ACT: Try to sign up again
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": already_signed_up_email}
    )
    
    # ASSERT: Check error response
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_fails_invalid_email_no_at_symbol(client, invalid_email):
    """
    ARRANGE: Fresh client, invalid email (no @)
    ACT: POST /activities/Chess Club/signup?email=invalidstudent
    ASSERT: Returns 422, 'Invalid email format'
    """
    # ARRANGE: client fixture provides fresh app state, invalid_email provided
    
    # ACT: Sign up with invalid email
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": invalid_email}
    )
    
    # ASSERT: Check validation error
    assert response.status_code == 422
    assert "Invalid email format" in response.json()["detail"]


def test_signup_fails_at_full_capacity(client):
    """
    ARRANGE: Fresh client, Tennis Club activity at near-full capacity (max=10, current=1)
    Fill Tennis Club to capacity, then attempt one more signup
    ACT: Sign up 9 more students to fill Tennis Club, then try 1 more
    ASSERT: 9th signup succeeds (200), 10th signup fails (400) with 'full capacity' message
    """
    # ARRANGE: client fixture provides fresh app state
    # Tennis Club: max_participants=10, participants=["alex@mergington.edu"]
    new_emails = [f"student{i}@mergington.edu" for i in range(1, 11)]
    
    # Fill Tennis Club to max capacity
    for email in new_emails[:9]:
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify Tennis Club is now at capacity (10 participants)
    activities_response = client.get("/activities")
    tennis_club = next(a for a in activities_response.json() if a["name"] == "Tennis Club")
    assert len(tennis_club["participants"]) == 10
    
    # ACT: Try to add 11th participant
    response = client.post(
        "/activities/Tennis Club/signup",
        params={"email": "overflow@mergington.edu"}
    )
    
    # ASSERT: Should fail with full capacity message
    assert response.status_code == 400
    assert "full capacity" in response.json()["detail"]


def test_signup_updates_participant_count(client, valid_email):
    """
    ARRANGE: Fresh client, activity with known participant count
    ACT: POST signup, then GET activities
    ASSERT: Participant count increases by 1
    """
    # ARRANGE: Get initial participant count
    initial_response = client.get("/activities")
    chess_club_initial = next(a for a in initial_response.json() if a["name"] == "Chess Club")
    initial_count = len(chess_club_initial["participants"])
    
    # ACT: Sign up new student
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": valid_email}
    )
    assert response.status_code == 200
    
    # Verify count increased
    verify_response = client.get("/activities")
    chess_club_updated = next(a for a in verify_response.json() if a["name"] == "Chess Club")
    assert len(chess_club_updated["participants"]) == initial_count + 1


def test_signup_response_format(client, valid_email):
    """
    ARRANGE: Fresh client, valid signup parameters
    ACT: POST /activities/Chess Club/signup?email=...
    ASSERT: Response contains message, activity, and email fields
    """
    # ARRANGE: client fixture provides fresh app state, valid_email provided
    
    # ACT: Sign up for activity
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": valid_email}
    )
    
    # ASSERT: Check response structure
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "activity" in data
    assert "email" in data
    assert data["activity"] == "Chess Club"
    assert data["email"] == valid_email
