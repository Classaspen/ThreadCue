from __future__ import annotations

import re
from datetime import datetime
import dateparser

DATE_PATTERNS = [
    r"\btoday\b", r"\btomorrow\b", r"\b(?:by|before)\s+(?:\w+|\d{1,2}/\d{1,2}/\d{2,4})(?:\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?)?",
    r"\bwithin\s+\d+\s+days?\b", r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\b",
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
]


def detect_deadline(text: str, base_date: datetime | None = None) -> datetime | None:
    matches = [match.group(0) for pattern in DATE_PATTERNS for match in re.finditer(pattern, text, re.IGNORECASE)]
    for extracted in matches:
        parsed = dateparser.parse(extracted, settings={"PREFER_DATES_FROM": "future", "RELATIVE_BASE": base_date})
        if parsed:
            return parsed
    return None
