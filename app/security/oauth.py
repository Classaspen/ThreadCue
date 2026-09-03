from __future__ import annotations

import json
from pathlib import Path
from .secrets import load_token, save_token


def authenticate_gmail(credentials_path: str | Path):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from app.providers.gmail import GmailProvider

    token = load_token()
    credentials = Credentials.from_authorized_user_info(json.loads(token)) if token else None
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    if not credentials or not credentials.valid:
        if not Path(credentials_path).exists():
            raise FileNotFoundError(f"Missing Gmail OAuth file: {credentials_path}")
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, GmailProvider.SCOPES)
        credentials = flow.run_local_server(port=0)
    save_token(credentials.to_json())
    from googleapiclient.discovery import build
    return build("gmail", "v1", credentials=credentials), credentials
