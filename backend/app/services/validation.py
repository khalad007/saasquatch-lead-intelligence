import re

# Reasonably strict email pattern without being a full RFC 5322 parser -
# good enough to catch scraper junk like "notarealemail" or blank cells.
EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Accepts common US formats: 213-555-0142, +1-213-555-0142, (213) 555-0142, 2135550142
PHONE_RE = re.compile(r"^\+?1?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$")


def is_valid_email(email: str | None) -> bool:
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_RE.match(email.strip()))


def is_valid_phone(phone: str | None) -> bool:
    if not phone or not isinstance(phone, str):
        return False
    return bool(PHONE_RE.match(phone.strip()))