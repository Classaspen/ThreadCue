from __future__ import annotations

from typing import Dict, List
from pydantic import BaseModel, Field


class Classification(BaseModel):
    categories: List[str] = Field(default_factory=list)
    matched_keywords: Dict[str, List[str]] = Field(default_factory=dict)
    is_new_lead: bool = False
    is_existing_client: bool = False
