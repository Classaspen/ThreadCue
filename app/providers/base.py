from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from app.domain.email import EmailMessage


class MailProvider(ABC):
    @abstractmethod
    def authenticate(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def fetch_messages(self, since: datetime) -> list[EmailMessage]:
        raise NotImplementedError
