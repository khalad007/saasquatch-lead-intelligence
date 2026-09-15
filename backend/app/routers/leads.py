import io
import csv
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from typing import Optional

from app.database import get_db
from app.models.lead import Lead
from app.schemas import LeadOut, UploadSummary, ScoreSummary
from app.services.validation import is_valid_email, is_valid_phone
from app.services.dedup import find_duplicate
from app.services.scoring import score_lead_with_ai

router = APIRouter(prefix="/leads", tags=["leads"])

REQUIRED_COLUMNS = {"company_name"}


@router.post("/upload", response_model=UploadSummary)
async def upload_leads(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only .csv files are supported")

    raw = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception as e:
        raise HTTPException(400, f"Could not parse CSV: {e}")

    df.columns = [c.strip().lower() for c in df.columns]
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(400, f"CSV missing required columns: {missing}")

    df = df.where(pd.notnull(df), None)

    existing_leads = [
        {"company_name": l.company_name, "domain": l.domain}
        for l in db.query(Lead.company_name, Lead.domain).all()
    ]

    inserted = 0
    duplicates_flagged = 0
    invalid_emails = 0
    invalid_phones = 0
    seen_in_batch: list[dict] = []

    for _, row in df.iterrows():
        candidate = {
            "company_name": row.get("company_name"),
            "domain": row.get("domain"),
        }
        if not candidate["company_name"]:
            continue

        dup_match = find_duplicate(candidate, existing_leads) or find_duplicate(candidate, seen_in_batch)

        email_valid = is_valid_email(row.get("email"))
        phone_valid = is_valid_phone(row.get("phone"))
        if not email_valid:
            invalid_emails += 1
        if not phone_valid:
            invalid_phones += 1
        if dup_match:
            duplicates_flagged += 1

        lead = Lead(
            company_name=candidate["company_name"],
            domain=row.get("domain"),
            industry=row.get("industry"),
            city=row.get("city"),
            country=row.get("country"),
            employee_count=_safe_int(row.get("employee_count")),
            estimated_revenue=_safe_float(row.get("estimated_revenue")),
            email=row.get("email"),
            phone=row.get("phone"),
            linkedin_url=row.get("linkedin_url"),
            source_confidence=_safe_float(row.get("source_confidence")),
            email_valid=email_valid,
            phone_valid=phone_valid,
            is_duplicate=bool(dup_match),
        )
        db.add(lead)
        db.flush()  # get lead.id without full commit

        if dup_match:
            lead.duplicate_of_id = dup_match.get("id")

        seen_in_batch.append({"company_name": lead.company_name, "domain": lead.domain, "id": lead.id})
        inserted += 1

    db.commit()

    return UploadSummary(
        total_rows=len(df),
        inserted=inserted,
        duplicates_flagged=duplicates_flagged,
        invalid_emails=invalid_emails,
        invalid_phones=invalid_phones,
    )


@router.post("/score", response_model=ScoreSummary)
def score_all_leads(db: Session = Depends(get_db), rescore: bool = False):
    query = db.query(Lead).filter(Lead.is_duplicate == False)  # noqa: E712
    if not rescore:
        query = query.filter(Lead.ai_score.is_(None))
    leads = query.all()

    hot = warm = cold = 0
    for lead in leads:
        result = score_lead_with_ai({
            "company_name": lead.company_name,
            "industry": lead.industry,
            "estimated_revenue": lead.estimated_revenue,
            "employee_count": lead.employee_count,
            "source_confidence": lead.source_confidence,
            "email_valid": lead.email_valid,
            "phone_valid": lead.phone_valid,
            "city": lead.city,
            "country": lead.country,
        })
        lead.ai_score = result["ai_score"]
        lead.ai_tier = result["ai_tier"]
        lead.ai_reasoning = result["ai_reasoning"]

        if lead.ai_tier == "Hot":
            hot += 1
        elif lead.ai_tier == "Warm":
            warm += 1
        else:
            cold += 1

    db.commit()
    return ScoreSummary(scored=len(leads), hot=hot, warm=warm, cold=cold)


@router.get("", response_model=list[LeadOut])
def list_leads(
    db: Session = Depends(get_db),
    industry: Optional[str] = None,
    tier: Optional[str] = None,
    min_score: Optional[float] = None,
    include_duplicates: bool = False,
    sort_by: str = Query("ai_score", enum=["ai_score", "estimated_revenue", "employee_count", "created_at"]),
    order: str = Query("desc", enum=["asc", "desc"]),
):
    query = db.query(Lead)
    if not include_duplicates:
        query = query.filter(Lead.is_duplicate == False)  # noqa: E712
    if industry:
        query = query.filter(Lead.industry.ilike(f"%{industry}%"))
    if tier:
        query = query.filter(Lead.ai_tier == tier)
    if min_score is not None:
        query = query.filter(Lead.ai_score >= min_score)

    sort_col = getattr(Lead, sort_by)
    query = query.order_by(asc(sort_col) if order == "asc" else desc(sort_col))

    return query.all()


@router.get("/export")
def export_leads(
    db: Session = Depends(get_db),
    industry: Optional[str] = None,
    tier: Optional[str] = None,
    min_score: Optional[float] = None,
):
    query = db.query(Lead).filter(Lead.is_duplicate == False)  # noqa: E712
    if industry:
        query = query.filter(Lead.industry.ilike(f"%{industry}%"))
    if tier:
        query = query.filter(Lead.ai_tier == tier)
    if min_score is not None:
        query = query.filter(Lead.ai_score >= min_score)
    leads = query.order_by(desc(Lead.ai_score)).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "company_name", "domain", "industry", "city", "country", "employee_count",
        "estimated_revenue", "email", "phone", "linkedin_url", "ai_score", "ai_tier", "ai_reasoning",
    ])
    for l in leads:
        writer.writerow([
            l.company_name, l.domain, l.industry, l.city, l.country, l.employee_count,
            l.estimated_revenue, l.email, l.phone, l.linkedin_url, l.ai_score, l.ai_tier, l.ai_reasoning,
        ])
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=scored_leads.csv"},
    )


@router.delete("/reset")
def reset_leads(db: Session = Depends(get_db)):
    """Convenience endpoint for demo purposes: wipes all leads."""
    db.query(Lead).delete()
    db.commit()
    return {"status": "cleared"}


def _safe_int(val):
    try:
        return int(val) if val is not None else None
    except (ValueError, TypeError):
        return None


def _safe_float(val):
    try:
        return float(val) if val is not None else None
    except (ValueError, TypeError):
        return None