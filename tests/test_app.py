"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Basketball Team": {
            "description": "Join the school basketball team and compete in local tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu", "james@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Improve swimming techniques and train for competitions",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore various art mediums including painting, drawing, and sculpture",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["emily@mergington.edu", "lucas@mergington.edu"]
        },
        "Theater Club": {
            "description": "Perform in plays, learn acting techniques, and stage production",
            "schedule": "Fridays, 3:30 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking skills through competitive debates",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["mia@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science and engineering challenges at regional competitions",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ethan@mergington.edu", "isabella@mergington.edu"]
        },
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
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRoot:
    """Test root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Basketball Team" in data
        assert "Swimming Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_structure(self, client):
        """Test that activity structure is correct"""
        response = client.get("/activities")
        data = response.json()
        
        basketball = data["Basketball Team"]
        assert "description" in basketball
        assert "schedule" in basketball
        assert "max_participants" in basketball
        assert "participants" in basketball
        assert basketball["max_participants"] == 15
        assert isinstance(basketball["participants"], list)


class TestSignupForActivity:
    """Test POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up newstudent@mergington.edu for Chess Club" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_fails(self, client):
        """Test that duplicate signup fails"""
        # First signup should succeed
        response = client.post(
            "/activities/Swimming%20Club/signup?email=sarah@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup for non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestUnregisterFromActivity:
    """Test DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        # Verify participant exists
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "alex@mergington.edu" in activities_data["Basketball Team"]["participants"]
        
        # Unregister
        response = client.delete(
            "/activities/Basketball%20Team/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered alex@mergington.edu from Basketball Team" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "alex@mergington.edu" not in activities_data["Basketball Team"]["participants"]
    
    def test_unregister_not_registered_fails(self, client):
        """Test that unregistering a non-registered participant fails"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregistering from non-existent activity fails"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestWorkflowIntegration:
    """Test complete signup and unregister workflow"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test complete workflow: signup -> verify -> unregister -> verify"""
        email = "workflow@mergington.edu"
        activity = "Art Studio"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data[activity]["participants"])
        
        # Signup
        signup_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify participant was added
        after_signup = client.get("/activities")
        after_signup_data = after_signup.json()
        assert email in after_signup_data[activity]["participants"]
        assert len(after_signup_data[activity]["participants"]) == initial_count + 1
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify participant was removed
        after_unregister = client.get("/activities")
        after_unregister_data = after_unregister.json()
        assert email not in after_unregister_data[activity]["participants"]
        assert len(after_unregister_data[activity]["participants"]) == initial_count
