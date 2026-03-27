"""
Integration tests for multi-step workflows.

Verifies:
- Signup → verify in list → delete → verify removed flow
- Multiple students signing up to same activity
- GET reflects signup/delete changes
- Complex activity state transitions
"""

import pytest


def test_signup_verify_delete_workflow(client, valid_email):
    """
    ARRANGE: Fresh client, valid email
    ACT: 1) Sign up, 2) Verify in list, 3) Delete, 4) Verify removed
    ASSERT: Each step succeeds with expected results
    """
    # ARRANGE: client fixture provides fresh app state, valid_email provided
    activity_name = "Chess Club"
    
    # ACT STEP 1: Sign up
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": valid_email}
    )
    # ASSERT Step 1: Signup succeeds
    assert signup_response.status_code == 200
    
    # ACT STEP 2: Verify email is in participants list
    get_response1 = client.get("/activities")
    activity = next(a for a in get_response1.json() if a["name"] == activity_name)
    # ASSERT Step 2: Email is in list
    assert valid_email in activity["participants"]
    
    # ACT STEP 3: Delete from activity
    delete_response = client.delete(
        f"/activities/{activity_name}/participants/{valid_email}"
    )
    # ASSERT Step 3: Delete succeeds
    assert delete_response.status_code == 200
    
    # ACT STEP 4: Verify email is removed
    get_response2 = client.get("/activities")
    activity_after = next(a for a in get_response2.json() if a["name"] == activity_name)
    # ASSERT Step 4: Email is no longer in list
    assert valid_email not in activity_after["participants"]


def test_multiple_students_signup_same_activity(client):
    """
    ARRANGE: Fresh client, 5 different valid emails
    ACT: Sign up all 5 students to same activity
    ASSERT: All 5 are in the participants list
    """
    # ARRANGE: client fixture provides fresh app state
    activity_name = "Programming Class"
    emails = [f"student{i}@mergington.edu" for i in range(1, 6)]
    initial_response = client.get("/activities")
    activity_initial = next(a for a in initial_response.json() if a["name"] == activity_name)
    initial_count = len(activity_initial["participants"])
    
    # ACT: Sign up all 5 students
    for email in emails:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # ASSERT: All are in the list
    verify_response = client.get("/activities")
    activity_final = next(a for a in verify_response.json() if a["name"] == activity_name)
    for email in emails:
        assert email in activity_final["participants"]
    
    # Verify count increased by 5
    assert len(activity_final["participants"]) == initial_count + 5


def test_signup_and_delete_multiple_users(client):
    """
    ARRANGE: Fresh client, 3 users
    ACT: Sign up 3 users, delete once, verify 2 remain, delete again, verify 1 remains
    ASSERT: Participant list matches expected state after each operation
    """
    # ARRANGE: client fixture provides fresh app state
    activity_name = "Gym Class"
    emails = ["new1@mergington.edu", "new2@mergington.edu", "new3@mergington.edu"]
    
    # Get initial state
    initial_response = client.get("/activities")
    activity_initial = next(a for a in initial_response.json() if a["name"] == activity_name)
    initial_participants = set(activity_initial["participants"])
    
    # ACT: Sign up all
    for email in emails:
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Verify all signed up
    resp = client.get("/activities")
    activity = next(a for a in resp.json() if a["name"] == activity_name)
    for email in emails:
        assert email in activity["participants"]
    
    # ACT: Delete first user
    client.delete(f"/activities/{activity_name}/participants/{emails[0]}")
    
    # ASSERT: First user gone, other 2 remain
    resp = client.get("/activities")
    activity = next(a for a in resp.json() if a["name"] == activity_name)
    assert emails[0] not in activity["participants"]
    assert emails[1] in activity["participants"]
    assert emails[2] in activity["participants"]
    
    # ACT: Delete second user
    client.delete(f"/activities/{activity_name}/participants/{emails[1]}")
    
    # ASSERT: First 2 gone, only third remains
    resp = client.get("/activities")
    activity = next(a for a in resp.json() if a["name"] == activity_name)
    assert emails[0] not in activity["participants"]
    assert emails[1] not in activity["participants"]
    assert emails[2] in activity["participants"]


def test_get_activities_reflects_changes(client, valid_email):
    """
    ARRANGE: Fresh client, activity with known initial state
    ACT: Signup, GET activities, Delete, GET activities again
    ASSERT: available_spots decreases on signup, increases on delete
    """
    # ARRANGE: client fixture provides fresh app state
    activity_name = "Tennis Club"
    
    # Get initial available spots
    resp = client.get("/activities")
    activity = next(a for a in resp.json() if a["name"] == activity_name)
    initial_spots = activity["available_spots"]
    
    # ACT: Sign up
    client.post(f"/activities/{activity_name}/signup", params={"email": valid_email})
    
    # ASSERT: available spots decreased by 1
    resp = client.get("/activities")
    activity = next(a for a in resp.json() if a["name"] == activity_name)
    assert activity["available_spots"] == initial_spots - 1
    
    # ACT: Delete
    client.delete(f"/activities/{activity_name}/participants/{valid_email}")
    
    # ASSERT: available spots restored
    resp = client.get("/activities")
    activity = next(a for a in resp.json() if a["name"] == activity_name)
    assert activity["available_spots"] == initial_spots


def test_capacity_enforcement_prevents_overfill(client):
    """
    ARRANGE: Fresh client, isolated activity with small capacity
    ACT: Fill to max - 1, verify next signup succeeds, verify signup after full fails
    ASSERT: Activity never exceeds max_participants
    """
    # ARRANGE: Use Tennis Club (max=10, current=1)
    activity_name = "Tennis Club"
    
    # Get current state
    resp = client.get("/activities")
    activity = next(a for a in resp.json() if a["name"] == activity_name)
    current_count = len(activity["participants"])
    max_participants = activity["max_participants"]
    spots_to_fill = max_participants - current_count
    
    # ACT: Fill remaining spots
    emails = [f"new{i}@mergington.edu" for i in range(spots_to_fill)]
    for email in emails:
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        assert response.status_code == 200
    
    # ASSERT: Activity is at max
    resp = client.get("/activities")
    activity = next(a for a in resp.json() if a["name"] == activity_name)
    assert len(activity["participants"]) == max_participants
    
    # ACT: Try to overfill
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "overflow@mergington.edu"}
    )
    
    # ASSERT: Fails with full capacity message
    assert response.status_code == 400
    assert "full capacity" in response.json()["detail"]
    
    # ASSERT: Count didn't change
    resp = client.get("/activities")
    activity = next(a for a in resp.json() if a["name"] == activity_name)
    assert len(activity["participants"]) == max_participants


def test_delete_frees_capacity_for_new_signup(client):
    """
    ARRANGE: Fresh client, full activity, new student ready
    ACT: Delete one student, sign up new student
    ASSERT: New student successfully replaces deleted student
    """
    # ARRANGE: Get a nearly-full activity and fill it
    activity_name = "Programming Class"
    
    # Get activity and see how many spots available
    resp = client.get("/activities")
    activity = next(a for a in resp.json() if a["name"] == activity_name)
    initial_count = len(activity["participants"])
    max_participants = activity["max_participants"]
    
    # Fill to capacity
    fill_emails = [f"fill{i}@mergington.edu" for i in range(max_participants - initial_count)]
    for email in fill_emails:
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Verify at capacity
    resp = client.get("/activities")
    activity = next(a for a in resp.json() if a["name"] == activity_name)
    assert len(activity["participants"]) == max_participants
    participant_before_delete = activity["participants"][0]
    
    # ACT: Delete one
    client.delete(f"/activities/{activity_name}/participants/{participant_before_delete}")
    
    # ASSERT: Capacity has opened
    resp = client.get("/activities")
    activity = next(a for a in resp.json() if a["name"] == activity_name)
    assert len(activity["participants"]) == max_participants - 1
    
    # ACT: Sign up new student
    new_email = "replacement@mergington.edu"
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email}
    )
    
    # ASSERT: New signup succeeds
    assert response.status_code == 200
    assert new_email in response.json().get("email", "")
    
    # Verify count is back to max
    resp = client.get("/activities")
    activity = next(a for a in resp.json() if a["name"] == activity_name)
    assert len(activity["participants"]) == max_participants
    assert new_email in activity["participants"]
