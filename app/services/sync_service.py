from __future__ import annotations

from datetime import datetime, timedelta, timezone
from app.providers.base import MailProvider
from app.db.repository import Repository
from .analysis_service import AnalysisService


class SyncService:
    def __init__(self, provider: MailProvider, repository: Repository, analyzer: AnalysisService):
        self.provider = provider
        self.repository = repository
        self.analyzer = analyzer

    def sync(self, days: int = 7):
        since = datetime.now(timezone.utc) - timedelta(days=days)
        messages = self.provider.fetch_messages(since)
        self.repository.upsert_emails(messages)
        analyses = self.analyzer.analyze(messages)
        for analysis in analyses:
            self.repository.save_analysis(analysis)
        return analyses
