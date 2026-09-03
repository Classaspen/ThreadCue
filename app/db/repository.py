from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.domain.email import EmailMessage
from app.domain.thread import ThreadAnalysis
from .models import EmailRecord, ThreadRecord


class Repository:
    def __init__(self, session: Session):
        self.session = session

    def upsert_emails(self, messages: list[EmailMessage]) -> None:
        for message in messages:
            record = self.session.get(EmailRecord, message.id)
            values = message.model_dump()
            if record is None:
                self.session.add(EmailRecord(**values))
            else:
                for key, value in values.items():
                    setattr(record, key, value)
        self.session.commit()

    def save_analysis(self, analysis: ThreadAnalysis) -> None:
        record = self.session.get(ThreadRecord, analysis.thread_id)
        values = analysis.model_dump(exclude={"messages", "last_message", "is_new_lead", "is_existing_client", "sender_is_vip"})
        if record is None:
            self.session.add(ThreadRecord(**values))
        else:
            for key, value in values.items():
                setattr(record, key, value)
        self.session.commit()

    def list_analyses(self) -> list[ThreadRecord]:
        return list(self.session.scalars(select(ThreadRecord).order_by(ThreadRecord.attention_score.desc())))
