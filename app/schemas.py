from typing import Literal

from pydantic import BaseModel, Field, field_validator

Goal = Literal["weight loss", "muscle gain", "general wellness", "flexibility"]
Intensity = Literal["low", "medium", "high"]
Experience = Literal["beginner", "intermediate", "advanced"]


class UserInput(BaseModel):
    user_id: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=2, max_length=120)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, le=500)
    goal: Goal
    intensity: Intensity
    experience: Experience = "beginner"

    @field_validator("user_id", "name")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty")
        return value


class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=80)
    feedback: str = Field(min_length=3, max_length=2000)


class PlanResponse(BaseModel):
    user_id: str
    name: str
    goal: str
    intensity: str
    experience: str
    workout_plan: str
    nutrition_tip: str
