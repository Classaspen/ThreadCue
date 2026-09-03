from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from .email import EmailMessage


class ThreadState(str, Enum):
    WAITING_ON_CUSTOMER = "WAITING_ON_CUSTOMER"
    WAITING_ON_USER = "WAITING_ON_USER"
    QUOTE_REQUIRED = "QUOTE_REQUIRED"
    QUOTE_FOLLOW_UP = "QUOTE_FOLLOW_UP"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    COMPLETE = "COMPLETE"


class ThreadAnalysis(BaseModel):
    thread_id: str
    subject: str
    messages: List[EmailMessage] = Field(default_factory=list)
    last_message: EmailMessage
    state: ThreadState
    categories: List[str] = Field(default_factory=list)
    requires_action: bool = False
    deadline: Optional[datetime] = None
    is_overdue: bool = False
    is_new_lead: bool = False
    is_existing_client: bool = False
    sender_is_vip: bool = False
    attention_score: int = 0
    priority: str = "LOW"
    reasons: List[str] = Field(default_factory=list)

    @property
    def last_activity(self) -> datetime:
        return self.last_message.received_at
