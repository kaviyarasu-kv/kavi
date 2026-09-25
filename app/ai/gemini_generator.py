from app.ai.gemini_client import get_client
from app.config import get_settings
from app.schemas import UserInput


SYSTEM_INSTRUCTION = """
You are FitBuddy, a careful fitness-planning assistant.
Create practical, conservative fitness plans for general wellness.
Do not diagnose, prescribe treatment, or promise medical outcomes.
Respect the user's age, weight, goal, intensity and experience.
Use bodyweight or common gym exercises. Include warm-up, main workout,
cool-down/recovery, sets/reps or duration, and rest guidance.
The result must be easy to follow for seven days.
If a request appears unsafe, recommend professional medical/fitness guidance
instead of providing an aggressive routine.
"""


def generate_workout_fallback(user: UserInput) -> str:
    goal = user.goal.lower()
    intensity = user.intensity.lower()
    experience = user.experience.lower()

    focus_map = {
        "weight loss": "steady calorie burn and conditioning",
        "muscle gain": "controlled strength work and progressive overload",
        "general wellness": "mobility, strength, and recovery",
        "flexibility": "mobility, range of motion, and posture",
    }

    intensity_map = {
        "low": "light to moderate effort with plenty of recovery",
        "medium": "moderate effort with controlled pacing",
        "high": "higher effort, but still safe and sustainable",
    }

    days = []
    for day in range(1, 8):
        if goal == "weight loss":
            primary = "brisk walk or bike intervals"
            secondary = "bodyweight circuit"
        elif goal == "muscle gain":
            primary = "strength circuit with compound movements"
            secondary = "light hypertrophy work"
        elif goal == "flexibility":
            primary = "mobility flow and stretching"
            secondary = "balance and posture work"
        else:
            primary = "full-body functional circuit"
            secondary = "core and mobility work"

        if day % 2 == 0:
            main = secondary
        else:
            main = primary

        days.append(
            f"Day {day}:\n"
            f"- Focus: {focus_map.get(goal, 'overall fitness')}\n"
            f"- Warm-up: 5-10 minutes of marching, arm circles, and light mobility.\n"
            f"- Main workout: {main} for 20-35 minutes. Use {intensity_map.get(intensity, 'steady effort')} and stop 1-2 reps before failure.\n"
            f"- Cool-down: 5-10 minutes of easy walking, stretching, and breathing.\n"
            f"- Recovery: Drink water and keep the next session at a comfortable pace.\n"
        )

    header = (
        f"Fallback 7-day plan for {user.name} ({experience.title()} / {user.goal.title()} / "
        f"{user.intensity.title()} intensity)\n"
        "This safe backup plan is designed to keep movement consistent when the AI service is temporarily unavailable.\n\n"
    )
    return header + "\n".join(days)


def generate_workout_gemini(user: UserInput) -> str:
    settings = get_settings()
    client = get_client()

    prompt = f"""
Create a personalized 7-day workout plan for:
Name: {user.name}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Preferred intensity: {user.intensity}
Experience: {user.experience}

Format:
Day 1 through Day 7.
For each day include:
- Focus
- Warm-up (5-10 minutes)
- Main workout with exercise, sets/reps or duration, and rest
- Cool-down/recovery
- One short safety note when useful

Keep the plan realistic and avoid extreme calorie-burning or unsafe training.
Do not include medication or supplement prescriptions.
"""

    response = client.models.generate_content(
        model=settings.workout_model,
        contents=prompt,
        config={
            "system_instruction": SYSTEM_INSTRUCTION,
            "temperature": 0.6,
            "max_output_tokens": 5000,
        },
    )

    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty workout plan.")
    return text
