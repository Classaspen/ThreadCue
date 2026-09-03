from __future__ import annotations

import re
from app.domain.action import ActionItem
from app.domain.email import EmailMessage
from .rules import ACTION_PATTERNS


def detect_actions(message: EmailMessage) -> list[ActionItem]:
    text = f"{message.subject}\n{message.body}"
    return [ActionItem(phrase=match.group(0), source_email_id=message.id) for pattern in ACTION_PATTERNS for match in re.finditer(pattern, text, flags=re.IGNORECASE)]
