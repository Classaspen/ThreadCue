from __future__ import annotations

from app.domain.thread import ThreadAnalysis


class AttentionService:
    @staticmethod
    def sort(analyses: list[ThreadAnalysis]) -> list[ThreadAnalysis]:
        return sorted(analyses, key=lambda item: (item.attention_score, item.last_activity), reverse=True)
