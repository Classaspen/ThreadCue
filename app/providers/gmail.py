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
        self.account_email = None

    def authenticate(self) -> bool:
        from app.security.oauth import authenticate_gmail
        self.service, self.token = authenticate_gmail(self.credentials_path)
        profile = self.service.users().getProfile(userId="me").execute()
        self.account_email = profile.get("emailAddress")
        if not self.account_email:
            raise RuntimeError("Gmail did not return the authenticated account")
        return self.service is not None

    def fetch_messages(self, since: datetime) -> list[EmailMessage]:
        if self.service is None:
            raise RuntimeError("Gmail is not authenticated")
        query = f"after:{int(since.timestamp())}"
        messages = []
        page_token = None
        while True:
            request = self.service.users().messages().list(userId="me", q=query, pageToken=page_token) if page_token else self.service.users().messages().list(userId="me", q=query)
            response = request.execute()
            messages.extend(
                self._to_message(self.service.users().messages().get(userId="me", id=item["id"], format="full").execute())
                for item in response.get("messages", [])
            )
            page_token = response.get("nextPageToken")
            if not page_token:
                return messages

    def _to_message(self, raw: dict) -> EmailMessage:
        headers = {item["name"].lower(): item["value"] for item in raw.get("payload", {}).get("headers", [])}
        body = self._extract_body(raw.get("payload", {}))
        received = parsedate_to_datetime(headers.get("date", "")) if headers.get("date") else datetime.now(timezone.utc)
        sender = parseaddr(headers.get("from", ""))[1]
        labels = raw.get("labelIds", [])
        recipients = [parseaddr(value.strip())[1] for value in re.split(r",|;", headers.get("to", "")) if parseaddr(value.strip())[1]]
        return EmailMessage(id=raw["id"], thread_id=raw.get("threadId", raw["id"]), subject=headers.get("subject", ""), sender=sender, recipients=recipients, body=body, received_at=received, is_outgoing="SENT" in labels or sender.lower() == (self.account_email or "").lower(), labels=labels)

    def _extract_body(self, payload: dict) -> str:
        if payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
        plain_parts = []
        html_parts = []
        parts = payload.get("parts", []) or [payload]
        for part in parts:
            if part.get("parts"):
                nested = self._extract_body(part)
                if nested:
                    plain_parts.append(nested)
                continue
            data = part.get("body", {}).get("data")
            if not data:
                continue
            decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            if part.get("mimeType") == "text/plain":
                plain_parts.append(decoded)
            elif part.get("mimeType") == "text/html":
                html_parts.append(decoded)
        if plain_parts:
            return "\n".join(plain_parts)
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape("\n".join(html_parts)))).strip()
