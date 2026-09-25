from app.ai.gemini_client import get_client
from app.config import get_settings


def update_workout_plan_fallback(original_plan: str, feedback: str, goal: str, intensity: str) -> str:
    summary = (
        f"Fallback revision based on feedback: '{feedback.strip()}'.\n"
        f"Goal: {goal}. Intensity: {intensity}.\n\n"
        "The revised plan keeps the original structure but reduces stress, adds recovery, and emphasizes steady progress.\n\n"
    )
    return summary + original_plan + "\n\n- Note: This fallback revision was created because the Gemini service was unavailable."


def update_workout_plan(original_plan: str, feedback: str, goal: str, intensity: str) -> str:
    settings = get_settings()
    client = get_client()

    prompt = f"""
Update the existing FitBuddy 7-day workout plan using the user's feedback.

Goal: {goal}
Intensity: {intensity}

USER FEEDBACK:
{feedback}

ORIGINAL PLAN:
{original_plan}

Return a complete revised Day 1-Day 7 plan, not only the changed days.
Preserve useful parts of the original plan while applying reasonable feedback.
Avoid unsafe or extreme exercise recommendations.
Include warm-up, main workout, rest, and recovery guidance.
"""

    response = client.models.generate_content(
        model=settings.workout_model,
        contents=prompt,
        config={
            "system_instruction": "You are a conservative fitness-plan revision assistant. Do not diagnose or prescribe medical treatment.",
            "temperature": 0.6,
            "max_output_tokens": 5000,
        },
    )

    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty updated plan.")
    return text
