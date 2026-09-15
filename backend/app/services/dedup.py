from rapidfuzz import fuzz

# Threshold above which two rows are considered the same company.
# Domain match is the strongest signal (scraped from different pages but
# same website); name similarity alone needs a higher bar since generic
# names ("Summit", "Vertex") can collide across unrelated companies.
NAME_SIMILARITY_THRESHOLD = 90


def normalize_domain(domain: str | None) -> str | None:
    if not domain:
        return None
    d = domain.strip().lower()
    d = d.replace("https://", "").replace("http://", "").replace("www.", "")
    return d.rstrip("/")


def is_duplicate(candidate: dict, existing: dict) -> bool:
    """
    Returns True if `candidate` lead is a duplicate of `existing` lead.
    Two signals, either is sufficient:
      1. Same normalized domain (strongest signal -- same company website)
      2. Fuzzy company-name similarity above threshold (catches
         "Brightpath Logistics" vs "Brightpath Logistics Inc")
    """
    cand_domain = normalize_domain(candidate.get("domain"))
    exist_domain = normalize_domain(existing.get("domain"))

    if cand_domain and exist_domain and cand_domain == exist_domain:
        return True

    cand_name = (candidate.get("company_name") or "").strip().lower()
    exist_name = (existing.get("company_name") or "").strip().lower()
    if cand_name and exist_name:
        score = fuzz.token_sort_ratio(cand_name, exist_name)
        if score >= NAME_SIMILARITY_THRESHOLD:
            return True

    return False


def find_duplicate(candidate: dict, existing_leads: list[dict]) -> dict | None:
    """Scan existing leads and return the first one that matches, or None."""
    for existing in existing_leads:
        if is_duplicate(candidate, existing):
            return existing
    return None