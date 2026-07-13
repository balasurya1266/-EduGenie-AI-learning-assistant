"""Pydantic schemas for request/response validation."""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    confirm_password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)


class ExplainRequest(BaseModel):
    topic: str = Field(..., min_length=2)
    level: str = "beginner"


class QuizRequest(BaseModel):
    topic: str = Field(..., min_length=2)
    difficulty: str = "medium"
    num_questions: int = Field(5, ge=1, le=20)


class SummaryRequest(BaseModel):
    text: str = Field(..., min_length=10)
    summary_type: str = "medium"


class LearningPathRequest(BaseModel):
    topic: str = Field(..., min_length=2)
    current_level: str = "beginner"
    weekly_hours: int = Field(5, ge=1, le=40)
    goal: str = Field(..., min_length=3)


class BookmarkRequest(BaseModel):
    query_id: str
    title: Optional[str] = None


class FlashcardRequest(BaseModel):
    topic: str = Field(..., min_length=2)
    num_cards: int = Field(10, ge=1, le=30)


class SettingsUpdate(BaseModel):
    dark_mode: Optional[bool] = None
    language: Optional[str] = None
    gemini_api_key: Optional[str] = None


class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
