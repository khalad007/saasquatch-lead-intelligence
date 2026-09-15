from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LeadOut(BaseModel):
    id: int
    company_name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    employee_count: Optional[int] = None
    estimated_revenue: Optional[float] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    source_confidence: Optional[float] = None
    email_valid: bool
    phone_valid: bool
    is_duplicate: bool
    duplicate_of_id: Optional[int] = None
    ai_score: Optional[float] = None
    ai_reasoning: Optional[str] = None
    ai_tier: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UploadSummary(BaseModel):
    total_rows: int
    inserted: int
    duplicates_flagged: int
    invalid_emails: int
    invalid_phones: int


class ScoreSummary(BaseModel):
    scored: int
    hot: int
    warm: int
    cold: int