"""
Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint.

Verifies:
- Successful removal of participant
- Activity not found error (404)
- Participant not found error (404)
- Invalid email format error (422)
- Email is removed from participants list
- Participant count decreases correctly
"""

import pytest


def test_delete_participant_success(client, already_signed_up_email):
    """
    ARRANGE: Fresh client, participant exists in Chess Club
    ACT: DELETE /activities/Chess Club/participants/michael@mergington.edu
    ASSERT: Returns 200, email removed from participants
    """
    # ARRANGE: client fixture provides fresh app state
    # already_signed_up_email (michael@mergington.edu) is in Chess Club
    
    # ACT: Remove participant
    response = client.delete(
        f"/activities/Chess Club/participants/{already_signed_up_email}"
    )
    
    # ASSERT: Check response and verify removal
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]
    
    # Verify email was removed
    activities_response = client.get("/activities")
    chess_club = next(a for a in activities_response.json() if a["name"] == "Chess Club")
    assert already_signed_up_email not in chess_club["participants"]


def test_delete_fails_activity_not_found(client, valid_email, nonexistent_activity):
    """
    ARRANGE: Fresh client, activity does not exist
    ACT: DELETE /activities/Nonexistent Activity/participants/...
    ASSERT: Returns 404, 'Activity not found'
    """
    # ARRANGE: client fixture provides fresh app state, nonexistent_activity provided
    
    # ACT: Try to remove from non-existent activity
    response = client.delete(
        f"/activities/{nonexistent_activity}/participants/{valid_email}"
    )
    
    # ASSERT: Check error response
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_delete_fails_participant_not_found(client, activity_name, valid_email):
    """
    ARRANGE: Fresh client, participant not in activity
    ACT: DELETE /activities/Chess Club/participants/student@mergington.edu
    ASSERT: Returns 404, 'Participant not found'
    """
    # ARRANGE: client fixture provides fresh app state
    # valid_email is not enrolled in Chess Club
    
    # ACT: Try to remove non-existent participant
    response = client.delete(
        f"/activities/{activity_name}/participants/{valid_email}"
    )
    
    # ASSERT: Check error response
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_delete_fails_invalid_email_no_at_symbol(client, invalid_email):
    """
    ARRANGE: Fresh client, invalid email (no @)
    ACT: DELETE /activities/Chess Club/participants/invalidstudent
    ASSERT: Returns 422, 'Invalid email format'
    """
    # ARRANGE: client fixture provides fresh app state, invalid_email provided
    
    # ACT: Try to remove with invalid email
    response = client.delete(
        f"/activities/Chess Club/participants/{invalid_email}"
    )
    
    # ASSERT: Check validation error
    assert response.status_code == 422
    assert "Invalid email format" in response.json()["detail"]


def test_delete_updates_participant_count(client, already_signed_up_email):
    """
    ARRANGE: Fresh client, participant in Chess Club, initial count known
    ACT: DELETE participant, then GET activities
    ASSERT: Participant count decreases by 1
    """
    # ARRANGE: Get initial participant count
    initial_response = client.get("/activities")
    chess_club_initial = next(a for a in initial_response.json() if a["name"] == "Chess Club")
    initial_count = len(chess_club_initial["participants"])
    assert initial_count >= 1  # Verify there's someone to delete
    
    # ACT: Remove participant
    response = client.delete(
        f"/activities/Chess Club/participants/{already_signed_up_email}"
    )
    assert response.status_code == 200
    
    # ASSERT: Verify count decreased
    verify_response = client.get("/activities")
    chess_club_updated = next(a for a in verify_response.json() if a["name"] == "Chess Club")
    assert len(chess_club_updated["participants"]) == initial_count - 1


def test_delete_response_format(client, already_signed_up_email):
    """
    ARRANGE: Fresh client, valid deletion parameters
    ACT: DELETE /activities/Chess Club/participants/...
    ASSERT: Response contains message with activity and email
    """
    # ARRANGE: client fixture provides fresh app state
    
    # ACT: Remove participant
    response = client.delete(
        f"/activities/Chess Club/participants/{already_signed_up_email}"
    )
    
    # ASSERT: Check response structure
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert already_signed_up_email in data["message"]
    assert "Chess Club" in data["message"]


def test_delete_twice_fails_second_time(client, already_signed_up_email):
    """
    ARRANGE: Fresh client, participant in activity
    ACT: Delete once (success), delete again (should fail)
    ASSERT: First delete 200, second delete 404 'Participant not found'
    """
    # ARRANGE: client fixture provides fresh app state
    
    # ACT & ASSERT: First deletion succeeds
    response1 = client.delete(
        f"/activities/Chess Club/participants/{already_signed_up_email}"
    )
    assert response1.status_code == 200
    
    # ACT & ASSERT: Second deletion fails (already removed)
    response2 = client.delete(
        f"/activities/Chess Club/participants/{already_signed_up_email}"
    )
    assert response2.status_code == 404
    assert "Participant not found" in response2.json()["detail"]


def test_delete_does_not_affect_other_participants(client):
    """
    ARRANGE: Fresh client, Chess Club has multiple participants
    ACT: Delete one participant
    ASSERT: Other participants remain in the list
    """
    # ARRANGE: Get initial participants
    initial_response = client.get("/activities")
    chess_club = next(a for a in initial_response.json() if a["name"] == "Chess Club")
    initial_participants = set(chess_club["participants"])
    participant_to_remove = list(initial_participants)[0]
    
    # ACT: Delete one participant
    response = client.delete(
        f"/activities/Chess Club/participants/{participant_to_remove}"
    )
    assert response.status_code == 200
    
    # ASSERT: Other participants still there
    verify_response = client.get("/activities")
    chess_club_after = next(a for a in verify_response.json() if a["name"] == "Chess Club")
    remaining_participants = set(chess_club_after["participants"])
    
    # Verify the removed person is gone
    assert participant_to_remove not in remaining_participants
    
    # Verify others are still there
    for participant in initial_participants - {participant_to_remove}:
        assert participant in remaining_participants
