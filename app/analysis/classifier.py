from __future__ import annotations

from pathlib import Path
import yaml
from app.domain.classification import Classification
from app.domain.email import EmailMessage
from .rules import DEFAULT_RULES


def load_rules(profile: str | Path | None = None) -> dict[str, list[str]]:
    if profile is None:
        return DEFAULT_RULES
    path = Path(profile)
    if not path.exists():
        return DEFAULT_RULES
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {name: values.get("keywords", []) for name, values in data.get("categories", {}).items()}


def classify(messages: list[EmailMessage], rules=None) -> Classification:
    rules = rules or DEFAULT_RULES
    text = "\n".join(f"{message.subject} {message.body}" for message in messages).lower()
    matched = {category: [word for word in words if word.lower() in text] for category, words in rules.items()}
    matched = {category: words for category, words in matched.items() if words}
    incoming = [message for message in messages if not message.is_outgoing]
    return Classification(categories=list(matched), matched_keywords=matched, is_new_lead=bool(incoming and any(category in matched for category in ("NEW_ENQUIRY", "BUYER"))), is_existing_client=any("invoice" in text or "existing client" in text for _ in [0]))
