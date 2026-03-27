"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, field_validator
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")


# Pydantic Models for request/response validation
class SignupRequest(BaseModel):
    """Request model for signup endpoint"""
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format (must contain @)"""
        if '@' not in v or not v.strip():
            raise ValueError('Invalid email format. Email must contain @')
        return v


class Activity(BaseModel):
    """Activity model with participants list"""
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    description: str
    schedule: str
    max_participants: int
    participants: list[str]


class ActivityResponse(BaseModel):
    """Response model for activity details"""
    name: str
    description: str
    schedule: str
    max_participants: int
    participants: list[str]
    available_spots: int

    @classmethod
    def from_activity(cls, name: str, activity_data: dict):
        """Create response from activity data"""
        available_spots = activity_data["max_participants"] - len(activity_data["participants"])
        return cls(
            name=name,
            description=activity_data["description"],
            schedule=activity_data["schedule"],
            max_participants=activity_data["max_participants"],
            participants=activity_data["participants"],
            available_spots=available_spots
        )


# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
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
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities", response_model=list[ActivityResponse])
def get_activities():
    """Get all activities with participant information"""
    return [
        ActivityResponse.from_activity(name, activity_data)
        for name, activity_data in activities.items()
    ]


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate email format
    try:
        signup_request = SignupRequest(email=email)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if signup_request.email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up for this activity")

    # Check capacity before adding
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is at full capacity")

    # Add student
    activity["participants"].append(signup_request.email)
    return {
        "message": f"Signed up {signup_request.email} for {activity_name}",
        "activity": activity_name,
        "email": signup_request.email
    }


@app.delete("/activities/{activity_name}/participants/{email}")
def remove_participant(activity_name: str, email: str):
    """Remove a student from an activity"""
    # Validate email format
    try:
        email_request = SignupRequest(email=email)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    # Validate participant exists
    if email_request.email not in activity["participants"]:
        raise HTTPException(status_code=404, detail="Participant not found")

    activity["participants"].remove(email_request.email)
    return {"message": f"Removed {email_request.email} from {activity_name}"}
