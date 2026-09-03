from __future__ import annotations

from datetime import datetime, timedelta
from app.domain.email import EmailMessage


def quote_followup_due(messages: list[EmailMessage], now: datetime, days: int = 3) -> bool:
    outbound = [m for m in messages if m.is_outgoing]
    incoming = [m for m in messages if not m.is_outgoing]
    if not outbound or not incoming or outbound[-1].received_at < incoming[-1].received_at:
        return False
    return now - outbound[-1].received_at >= timedelta(days=days)
