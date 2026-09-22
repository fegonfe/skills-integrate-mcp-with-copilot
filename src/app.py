"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
import unicodedata

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

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

# Searchable student directory. Enrollment records continue to use email until
# the dedicated student profile work in issue #9 is implemented.
students = [
    {"student_id": "MH1001", "name": "Amelia Nguyen", "email": "amelia@mergington.edu"},
    {"student_id": "MH1002", "name": "Áva García", "email": "ava@mergington.edu"},
    {"student_id": "MH1003", "name": "Benjamin Carter", "email": "benjamin@mergington.edu"},
    {"student_id": "MH1004", "name": "Charlotte Wilson", "email": "charlotte@mergington.edu"},
    {"student_id": "MH1005", "name": "Daniel Kim", "email": "daniel@mergington.edu"},
    {"student_id": "MH1006", "name": "Ella Thompson", "email": "ella@mergington.edu"},
    {"student_id": "MH1007", "name": "Emma Davis", "email": "emma@mergington.edu"},
    {"student_id": "MH1008", "name": "Harper Brown", "email": "harper@mergington.edu"},
    {"student_id": "MH1009", "name": "Henry Martinez", "email": "henry@mergington.edu"},
    {"student_id": "MH1010", "name": "James Anderson", "email": "james@mergington.edu"},
    {"student_id": "MH1011", "name": "John Taylor", "email": "john@mergington.edu"},
    {"student_id": "MH1012", "name": "Liam Thomas", "email": "liam@mergington.edu"},
    {"student_id": "MH1013", "name": "Mia Moore", "email": "mia@mergington.edu"},
    {"student_id": "MH1014", "name": "Michael Jackson", "email": "michael@mergington.edu"},
    {"student_id": "MH1015", "name": "Noah White", "email": "noah@mergington.edu"},
    {"student_id": "MH1016", "name": "Olivia Harris", "email": "olivia@mergington.edu"},
    {"student_id": "MH1017", "name": "Scarlett Martin", "email": "scarlett@mergington.edu"},
    {"student_id": "MH1018", "name": "Sophia Lee", "email": "sophia@mergington.edu"},
]

MAX_SEARCH_RESULTS = 10


def normalize_name(value: str) -> str:
    """Normalize names for case- and accent-insensitive comparison."""
    decomposed = unicodedata.normalize("NFKD", value)
    without_marks = "".join(
        character for character in decomposed
        if not unicodedata.combining(character)
    )
    return without_marks.replace("đ", "d").replace("Đ", "D").casefold()


def find_students(query: str) -> dict:
    """Find students by partial ID or partial normalized name."""
    cleaned_query = query.strip()
    if not cleaned_query:
        return {
            "query": "",
            "search_type": None,
            "results": [],
            "total_matches": 0,
            "has_more": False,
        }

    is_id_search = any(character.isdigit() for character in cleaned_query)
    if is_id_search:
        normalized_query = cleaned_query.upper()
        matches = [
            student for student in students
            if normalized_query in student["student_id"].upper()
        ]
        matches.sort(key=lambda student: (
            student["student_id"].upper() != normalized_query,
            student["student_id"],
        ))
        search_type = "student_id"
    else:
        normalized_query = normalize_name(cleaned_query)
        matches = [
            student for student in students
            if normalized_query in normalize_name(student["name"])
        ]
        matches.sort(key=lambda student: normalize_name(student["name"]))
        search_type = "name"

    total_matches = len(matches)
    return {
        "query": cleaned_query,
        "search_type": search_type,
        "results": matches[:MAX_SEARCH_RESULTS],
        "total_matches": total_matches,
        "has_more": total_matches > MAX_SEARCH_RESULTS,
    }


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.get("/students/search")
def search_students(q: str = ""):
    """Search students by student ID or name."""
    return find_students(q)


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
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
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
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
