from __future__ import annotations

import keyring

SERVICE_NAME = "attention-inbox"


def save_token(token: str) -> None:
    keyring.set_password(SERVICE_NAME, "gmail-oauth", token)


def load_token() -> str | None:
    return keyring.get_password(SERVICE_NAME, "gmail-oauth")


def delete_token() -> None:
    try:
        keyring.delete_password(SERVICE_NAME, "gmail-oauth")
    except keyring.errors.PasswordDeleteError:
        pass
