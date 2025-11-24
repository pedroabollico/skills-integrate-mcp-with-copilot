"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Cookie, Response, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
import json
import secrets
from typing import Optional
from pydantic import BaseModel

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Load teacher credentials from JSON file
def load_teachers():
    teachers_file = os.path.join(current_dir, "teachers.json")
    try:
        with open(teachers_file, 'r') as f:
            data = json.load(f)
            return data['teachers']
    except FileNotFoundError:
        print(f"Warning: {teachers_file} not found. No teachers will be able to log in.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {teachers_file}: {e}")
        return []

teachers = load_teachers()

# In-memory session storage (simple token-based auth)
# Note: Sessions will be lost on server restart. In production, use Redis or database.
SESSION_TIMEOUT = 8 * 3600  # 8 hours in seconds
SECURE_COOKIES = os.environ.get("SECURE_COOKIES", "false").lower() == "true"
active_sessions = {}


# Pydantic models for request bodies
class LoginRequest(BaseModel):
    username: str
    password: str

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
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.post("/auth/login")
def login(credentials: LoginRequest, response: Response):
    """Login endpoint for teachers"""
    # Verify credentials
    for teacher in teachers:
        if teacher['username'] == credentials.username and teacher['password'] == credentials.password:
            # Generate session token
            session_token = secrets.token_urlsafe(32)
            active_sessions[session_token] = credentials.username
            
            # Set cookie
            response.set_cookie(
                key="session_token",
                value=session_token,
                httponly=True,
                max_age=SESSION_TIMEOUT,
                samesite="lax",
                secure=SECURE_COOKIES  # Only send over HTTPS in production
            )
            return {"message": "Login successful", "username": credentials.username}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/auth/logout")
def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    """Logout endpoint"""
    if session_token and session_token in active_sessions:
        del active_sessions[session_token]
    
    response.delete_cookie(key="session_token")
    return {"message": "Logged out successfully"}


@app.get("/auth/verify")
def verify_session(session_token: Optional[str] = Cookie(None)):
    """Verify if user is authenticated"""
    if session_token and session_token in active_sessions:
        return {
            "authenticated": True,
            "username": active_sessions[session_token]
        }
    return {"authenticated": False}


def is_authenticated(session_token: Optional[str]) -> bool:
    """Helper function to check if user is authenticated"""
    return session_token is not None and session_token in active_sessions


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, session_token: Optional[str] = Cookie(None)):
    """Sign up a student for an activity - requires authentication"""
    # Check authentication
    if not is_authenticated(session_token):
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Only teachers can register students."
        )
    
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, session_token: Optional[str] = Cookie(None)):
    """Unregister a student from an activity - requires authentication"""
    # Check authentication
    if not is_authenticated(session_token):
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Only teachers can unregister students."
        )
    
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
