from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Plan, User
from app.schemas import FeedbackRequest, UserInput
from app.ai.gemini_flash_generator import (
    generate_nutrition_tip_fallback,
    generate_nutrition_tip_with_flash,
)
from app.ai.gemini_generator import generate_workout_fallback, generate_workout_gemini
from app.ai.updated_plan import update_workout_plan, update_workout_plan_fallback

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")


def error_page(request: Request, message: str, status_code: int = 400):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"error": message},
        status_code=status_code,
    )


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    experience: str = Form("beginner"),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(
            user_id=user_id,
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
            experience=experience,
        )
    except Exception as exc:
        return error_page(request, f"Please check your inputs: {exc}", 422)

    existing = db.scalar(select(User).where(User.user_id == data.user_id))
    if existing:
        user = existing
        user.name = data.name
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity
        user.experience = data.experience
    else:
        user = User(**data.model_dump())
        db.add(user)

    try:
        workout_plan = generate_workout_gemini(data)
        nutrition_tip = generate_nutrition_tip_with_flash(data.goal, data.age, data.weight)
    except Exception:
        workout_plan = generate_workout_fallback(data)
        nutrition_tip = generate_nutrition_tip_fallback(data.goal, data.age, data.weight)

    plan = Plan(
        user_id=data.user_id,
        original_plan=workout_plan,
        nutrition_tip=nutrition_tip,
    )
    db.add(plan)
    db.commit()

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "plan": plan,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
            "updated": False,
            "message": "Your personalized plan is ready.",
        },
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    if len(feedback.strip()) > settings.max_feedback_length:
        return error_page(request, "Feedback is too long.", 422)

    user = db.scalar(select(User).where(User.user_id == user_id.strip()))
    plan = db.scalar(
        select(Plan).where(Plan.user_id == user_id.strip()).order_by(Plan.id.desc())
    )

    if not user or not plan:
        return error_page(request, "User or workout plan not found.", 404)

    try:
        revised = update_workout_plan(
            plan.original_plan,
            feedback.strip(),
            user.goal,
            user.intensity,
        )
    except Exception:
        revised = update_workout_plan_fallback(
            plan.original_plan,
            feedback.strip(),
            user.goal,
            user.intensity,
        )

    plan.updated_plan = revised
    plan.feedback = feedback.strip()
    from datetime import datetime
    plan.updated_at = datetime.utcnow()
    db.commit()

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "plan": plan,
            "workout_plan": revised,
            "nutrition_tip": plan.nutrition_tip,
            "updated": True,
            "message": "Your plan has been updated using your feedback.",
        },
    )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(
    request: Request,
    admin_token: str = "",
    db: Session = Depends(get_db),
):
    settings = get_settings()
    if settings.admin_token and admin_token != settings.admin_token:
        return error_page(request, "Invalid admin token.", 403)

    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    plans = db.scalars(select(Plan).order_by(Plan.id.desc())).all()

    latest_plans = {}
    for plan in plans:
        latest_plans.setdefault(plan.user_id, plan)

    rows = [{"user": user, "plan": latest_plans.get(user.user_id)} for user in users]

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"rows": rows, "admin_token": admin_token},
    )


# JSON API: useful for Postman/mobile/frontend integration.
@router.post("/api/generate-workout")
def api_generate_workout(payload: UserInput, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.user_id == payload.user_id))
    if existing:
        user = existing
        for key, value in payload.model_dump().items():
            setattr(user, key, value)
    else:
        user = User(**payload.model_dump())
        db.add(user)

    try:
        workout = generate_workout_gemini(payload)
        tip = generate_nutrition_tip_with_flash(payload.goal, payload.age, payload.weight)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    plan = Plan(user_id=payload.user_id, original_plan=workout, nutrition_tip=tip)
    db.add(plan)
    db.commit()

    return {
        "user": payload.model_dump(),
        "workout_plan": workout,
        "nutrition_tip": tip,
    }


@router.post("/api/submit-feedback")
def api_submit_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.user_id == payload.user_id))
    plan = db.scalar(
        select(Plan).where(Plan.user_id == payload.user_id).order_by(Plan.id.desc())
    )
    if not user or not plan:
        raise HTTPException(status_code=404, detail="User or plan not found.")

    try:
        revised = update_workout_plan(
            plan.original_plan, payload.feedback, user.goal, user.intensity
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    plan.updated_plan = revised
    plan.feedback = payload.feedback
    from datetime import datetime
    plan.updated_at = datetime.utcnow()
    db.commit()

    return {"user_id": payload.user_id, "updated_plan": revised}
