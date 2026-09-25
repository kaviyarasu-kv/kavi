from app.ai.gemini_client import get_client
from app.config import get_settings


def generate_nutrition_tip_fallback(goal: str, age: int, weight: float) -> str:
    goal_text = goal.lower()
    if goal_text == "weight loss":
        focus = "Keep meals balanced with lean protein, fiber-rich vegetables, and controlled portions."
    elif goal_text == "muscle gain":
        focus = "Aim for protein at each meal and add a little extra carbohydrate around training sessions."
    elif goal_text == "flexibility":
        focus = "Prioritize hydration, regular meals, and recovery foods that support joint comfort."
    else:
        focus = "Choose colorful meals with protein, veggies, and enough carbs to sustain energy."

    return (
        f"Hydration is essential throughout the day, and you should keep meals consistent. {focus} "
        f"For a {age}-year-old at {weight} kg, aim for regular protein and fiber intake, and avoid skipping meals. "
        "This will help recovery, energy, and better workout consistency."
    )


def generate_nutrition_tip_with_flash(goal: str, age: int, weight: float) -> str:
    settings = get_settings()
    client = get_client()

    prompt = f"""
Give one concise nutrition or recovery tip for a fitness user.

Goal: {goal}
Age: {age}
Weight: {weight} kg

Requirements:
- 3-5 sentences maximum.
- Practical, general wellness advice.
- Mention hydration, balanced meals, protein/fiber or recovery when relevant.
- Do not prescribe a medical diet, medication, or exact therapeutic dosage.
- Encourage professional advice for medical conditions or special dietary needs.
"""

    response = client.models.generate_content(
        model=settings.nutrition_model,
        contents=prompt,
        config={
            "temperature": 0.4,
            "max_output_tokens": 500,
        },
    )

    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty nutrition tip.")
    return text
