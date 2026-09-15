from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from datetime import datetime
from app.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    # Raw scraped fields (what SaaSquatch's scraper would produce)
    company_name = Column(String, index=True, nullable=False)
    domain = Column(String, index=True, nullable=True)
    industry = Column(String, index=True, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    employee_count = Column(Integer, nullable=True)
    estimated_revenue = Column(Float, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    source_confidence = Column(Float, nullable=True)  # 0-1, from original scrape

    # Enrichment / validation fields we compute
    email_valid = Column(Boolean, default=False)
    phone_valid = Column(Boolean, default=False)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(Integer, nullable=True)

    # AI scoring fields
    ai_score = Column(Float, nullable=True)          # 0-100 priority score
    ai_reasoning = Column(Text, nullable=True)        # short explanation from Gemini
    ai_tier = Column(String, nullable=True)           # "Hot" / "Warm" / "Cold"

    created_at = Column(DateTime, default=datetime.utcnow)