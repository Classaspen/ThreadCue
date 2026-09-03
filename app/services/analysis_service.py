from __future__ import annotations

from collections import defaultdict
from app.analysis.attention import analyze_thread
from app.domain.email import EmailMessage


class AnalysisService:
    def __init__(self, rules=None, followup_days: int = 3):
        self.rules = rules
        self.followup_days = followup_days

    def analyze(self, messages: list[EmailMessage]):
        grouped = defaultdict(list)
        for message in messages:
            grouped[message.thread_id].append(message)
        return [analyze_thread(items, rules=self.rules, followup_days=self.followup_days) for items in grouped.values()]
