from __future__ import annotations

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class EmailMessage(BaseModel):
    id: str
    thread_id: str
    subject: str = ""
    sender: str = ""
    recipients: List[str] = Field(default_factory=list)
    body: str = ""
    received_at: datetime
    is_outgoing: bool = False
    labels: List[str] = Field(default_factory=list)
    provider: str = "gmail"
