"""
Pytest configuration and fixtures for FastAPI tests.

Provides:
- TestClient fixture with fresh app instance
- Sample test data (emails, activity names)
- Activity reset between tests
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """
    Create a test client with fresh app instance.
    Resets activities to initial state before each test.
    """
    # ARRANGE: Reset activities to initial state (fresh data for each test)
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Compete in basketball games and tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn and practice tennis skills",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["alex@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "grace@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Play instruments and perform in concerts",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["liam@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu"]
        }
    })
    
    # Create test client
    return TestClient(app)


# Test data fixtures
@pytest.fixture
def valid_email():
    """Sample valid email for tests"""
    return "student@mergington.edu"


@pytest.fixture
def invalid_email():
    """Sample invalid email (no @) for tests"""
    return "invalidstudent"


@pytest.fixture
def activity_name():
    """Sample activity name for tests"""
    return "Chess Club"


@pytest.fixture
def nonexistent_activity():
    """Activity name that doesn't exist"""
    return "Nonexistent Activity"


@pytest.fixture
def already_signed_up_email():
    """Email of student already signed up for Chess Club"""
    return "michael@mergington.edu"


@pytest.fixture
def full_capacity_activity():
    """Activity that would be at full capacity with another signup"""
    return "Tennis Club"  # max_participants=10, currently has 1


@pytest.fixture
def empty_activity():
    """Activity that exists but has no capacity issues"""
    return "Basketball Team"  # max_participants=15, currently has 1
