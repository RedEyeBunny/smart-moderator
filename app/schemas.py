from pydantic import BaseModel, EmailStr
from typing import Optional, Literal


class TextModerationIn(BaseModel):
    email: EmailStr
    text: str


class ImageModerationIn(BaseModel):
    email: EmailStr
    image_url: Optional[str] = None


class ModerationResultOut(BaseModel):
    classification: Literal["toxic", "spam", "harassment", "safe"]
    confidence: float
    reasoning: Optional[str] = None


class AnalyticsSummaryOut(BaseModel):
    user: EmailStr
    total: int
    safe: int
    flagged: int
    breakdown: dict
