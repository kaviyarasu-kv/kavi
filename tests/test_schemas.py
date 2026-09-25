from app.ai.gemini_flash_generator import generate_nutrition_tip_fallback
from app.ai.gemini_generator import generate_workout_fallback
from app.schemas import UserInput


def test_user_input_validation():
    user = UserInput(
        user_id="FB001",
        name="Kavi",
        age=21,
        weight=65,
        goal="muscle gain",
        intensity="medium",
        experience="beginner",
    )
    assert user.age == 21
    assert user.goal == "muscle gain"


def test_fallback_workout_and_nutrition_are_generated():
    user = UserInput(
        user_id="FB002",
        name="Aarav",
        age=28,
        weight=72,
        goal="general wellness",
        intensity="medium",
        experience="beginner",
    )

    workout = generate_workout_fallback(user)
    nutrition = generate_nutrition_tip_fallback(user.goal, user.age, user.weight)

    assert "Day 1" in workout
    assert "Day 7" in workout
    assert "hydration" in nutrition.lower()
