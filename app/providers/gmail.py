from __future__ import annotations

import base64
import html
import re
from datetime import datetime, timezone
from email.utils import parseaddr, parsedate_to_datetime
from pathlib import Path
from .base import MailProvider
from app.domain.email import EmailMessage


class GmailProvider(MailProvider):
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self, credentials_path: str | Path = "credentials.json", token=None):
        self.credentials_path = Path(credentials_path)
        self.token = token
        self.service = None

    def authenticate(self) -> bool:
        from app.security.oauth import authenticate_gmail
        self.service, self.token = authenticate_gmail(self.credentials_path)
        return self.service is not None

    def fetch_messages(self, since: datetime) -> list[EmailMessage]:
        if self.service is None:
            raise RuntimeError("Gmail is not authenticated")
        query = f"after:{int(since.timestamp())}"
        response = self.service.users().messages().list(userId="me", q=query).execute()
        return [self._to_message(self.service.users().messages().get(userId="me", id=item["id"], format="full").execute()) for item in response.get("messages", [])]

    def _to_message(self, raw: dict) -> EmailMessage:
        headers = {item["name"].lower(): item["value"] for item in raw.get("payload", {}).get("headers", [])}
        body = self._extract_body(raw.get("payload", {}))
        received = parsedate_to_datetime(headers.get("date", "")) if headers.get("date") else datetime.now(timezone.utc)
        sender = parseaddr(headers.get("from", ""))[1]
        labels = raw.get("labelIds", [])
        return EmailMessage(id=raw["id"], thread_id=raw.get("threadId", raw["id"]), subject=headers.get("subject", ""), sender=sender, recipients=[parseaddr(headers.get("to", ""))[1]], body=body, received_at=received, is_outgoing="SENT" in labels, labels=labels)

    def _extract_body(self, payload: dict) -> str:
        if payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        return re.sub(r"<[^>]+>", " ", html.unescape(payload.get("body", {}).get("data", "")))
