from fastapi.testclient import TestClient

from app.main import app


def test_home_page():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_generate_workout_route_returns_fallback_plan():
    client = TestClient(app)
    response = client.post(
        "/generate-workout",
        data={
            "user_id": "FB-FALLBACK",
            "name": "Fallback User",
            "age": 27,
            "weight": 68,
            "goal": "general wellness",
            "intensity": "medium",
            "experience": "beginner",
        },
    )

    assert response.status_code == 200
    assert "Fallback 7-day plan" in response.text or "Your personalized plan is ready." in response.text
