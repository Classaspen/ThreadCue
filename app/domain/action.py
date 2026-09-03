from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ActionItem(BaseModel):
    phrase: str
    source_email_id: str
    deadline: Optional[datetime] = None
    completed: bool = False
