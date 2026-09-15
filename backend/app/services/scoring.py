import os
import json
import math
import logging

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

_gemini_model = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:  # pragma: no cover
        logger.warning("Gemini not available, falling back to rule-based scoring: %s", e)
        _gemini_model = None


def rule_based_score(lead: dict) -> float:
    """
    Deterministic, explainable baseline score (0-100) from firmographic data.
    This is the score a sales manager could sanity-check by hand -- the AI
    layer on top only adds reasoning and nudges within a bounded range,
    it never overrides business logic outright.

    Weights:
      - Revenue (log-scaled)   : 35%
      - Employee count (log)   : 20%
      - Source confidence      : 25%
      - Data completeness      : 20% (valid email/phone present)
    """
    revenue = lead.get("estimated_revenue") or 0
    employees = lead.get("employee_count") or 0
    confidence = lead.get("source_confidence") or 0
    email_valid = lead.get("email_valid", False)
    phone_valid = lead.get("phone_valid", False)

    # log-scale so a $28M company doesn't dwarf everything else linearly
    revenue_component = min(math.log10(revenue + 1) / 8, 1.0) * 35
    employee_component = min(math.log10(employees + 1) / 3, 1.0) * 20
    confidence_component = min(max(confidence, 0), 1.0) * 25
    completeness_component = (int(email_valid) + int(phone_valid)) / 2 * 20

    score = revenue_component + employee_component + confidence_component + completeness_component
    return round(min(score, 100.0), 1)


def tier_from_score(score: float) -> str:
    if score >= 70:
        return "Hot"
    if score >= 40:
        return "Warm"
    return "Cold"


def _fallback_reasoning(lead: dict, score: float, tier: str) -> str:
    parts = []
    if lead.get("estimated_revenue"):
        parts.append(f"${lead['estimated_revenue']:,.0f} est. revenue")
    if lead.get("employee_count"):
        parts.append(f"{lead['employee_count']} employees")
    if lead.get("source_confidence") is not None:
        parts.append(f"{lead['source_confidence']*100:.0f}% source confidence")
    detail = ", ".join(parts) if parts else "limited firmographic data"
    return f"{tier} priority ({score}/100) based on {detail}."


def score_lead_with_ai(lead: dict) -> dict:
    """
    Returns {"ai_score": float, "ai_tier": str, "ai_reasoning": str}
    Uses a rule-based score as the anchor, then (if Gemini is configured)
    asks the model for a short, sales-ready justification a rep could
    read in 3 seconds -- and lets it apply a small +/-10 point adjustment
    if it spots a qualitative signal the formula can't see (e.g. industry
    fit, "AI/fintech" naming suggesting a hot vertical).
    """
    base_score = rule_based_score(lead)
    base_tier = tier_from_score(base_score)

    if not _gemini_model:
        return {
            "ai_score": base_score,
            "ai_tier": base_tier,
            "ai_reasoning": _fallback_reasoning(lead, base_score, base_tier),
        }

    prompt = f"""You are a B2B sales prioritization assistant. A rule-based
system has already scored this lead {base_score}/100 ({base_tier}) using
revenue, employee count, and data confidence.

Lead data:
- Company: {lead.get('company_name')}
- Industry: {lead.get('industry')}
- Estimated revenue: {lead.get('estimated_revenue')}
- Employees: {lead.get('employee_count')}
- Source confidence: {lead.get('source_confidence')}
- Location: {lead.get('city')}, {lead.get('country')}

Task: Review the base score. You may adjust it by at most 10 points up or
down if you see a genuine qualitative signal (e.g. a high-growth industry,
a strong ICP fit for a B2B SaaS lead-gen tool). Otherwise keep it close to
the base score. Respond with ONLY valid JSON, no markdown, no preamble:
{{"final_score": <0-100 number>, "tier": "Hot" | "Warm" | "Cold", "reasoning": "<one sentence, sales-ready, under 25 words>"}}
"""

    try:
        response = _gemini_model.generate_content(prompt)
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(text)

        final_score = float(parsed["final_score"])
        # Safety clamp: never let the model wander more than 10pts from the
        # rule-based anchor, and never outside 0-100.
        final_score = max(min(final_score, base_score + 10), base_score - 10)
        final_score = max(0.0, min(100.0, round(final_score, 1)))

        return {
            "ai_score": final_score,
            "ai_tier": parsed.get("tier", tier_from_score(final_score)),
            "ai_reasoning": parsed.get("reasoning", _fallback_reasoning(lead, final_score, base_tier)),
        }
    except Exception as e:
        logger.warning("Gemini scoring failed, using rule-based fallback: %s", e)
        return {
            "ai_score": base_score,
            "ai_tier": base_tier,
            "ai_reasoning": _fallback_reasoning(lead, base_score, base_tier),
        }