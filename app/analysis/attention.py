from __future__ import annotations

from datetime import datetime, timezone
from app.domain.email import EmailMessage
from app.domain.thread import ThreadAnalysis, ThreadState
from .action_detector import detect_actions
from .classifier import classify
from .deadline_detector import detect_deadline
from .followup_detector import quote_followup_due
from .priority import priority_for
from .rules import QUOTE_WORDS


def analyze_thread(messages: list[EmailMessage], now: datetime | None = None, rules=None, followup_days: int = 3) -> ThreadAnalysis:
    if not messages:
        raise ValueError("Cannot analyze an empty thread")
    now = now or datetime.now(timezone.utc)
    ordered = sorted(messages, key=lambda message: message.received_at)
    last = ordered[-1]
    text = "\n".join(f"{message.subject} {message.body}" for message in ordered)
    classification = classify(ordered, rules)
    actions = [action for message in ordered for action in detect_actions(message)]
    deadline = detect_deadline(text, now)
    if deadline and deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    overdue = bool(deadline and deadline < now)
    incoming = [message for message in ordered if not message.is_outgoing]
    quote_request = bool(incoming and any(word in text.lower() for word in QUOTE_WORDS))
    has_outbound_after_incoming = bool(incoming and any(message.is_outgoing and message.received_at > incoming[-1].received_at for message in ordered))
    waiting_on_user = not last.is_outgoing
    followup_due = quote_followup_due(ordered, now, followup_days)
    if quote_request and not has_outbound_after_incoming:
        state = ThreadState.QUOTE_REQUIRED
    elif followup_due and quote_request:
        state = ThreadState.QUOTE_FOLLOW_UP
    elif actions and waiting_on_user:
        state = ThreadState.ACTION_REQUIRED
    elif waiting_on_user:
        state = ThreadState.WAITING_ON_USER
    else:
        state = ThreadState.WAITING_ON_CUSTOMER

    score = 0
    reasons = []
    def add(points: int, reason: str):
        nonlocal score
        score += points
        reasons.append(f"+{points} {reason}")
    if classification.is_new_lead: add(30, "New lead")
    if waiting_on_user: add(25, "Waiting for your reply")
    if state == ThreadState.QUOTE_REQUIRED: add(25, "Quote request detected")
    if state == ThreadState.QUOTE_FOLLOW_UP: add(20, "Quote follow-up due")
    if deadline: add(15, "Deadline detected")
    if overdue: add(30, "Deadline overdue")
    if classification.is_existing_client: add(15, "Existing customer")
    if actions: add(15, "Action phrase detected")
    return ThreadAnalysis(thread_id=last.thread_id, subject=last.subject, messages=ordered, last_message=last, state=state, categories=classification.categories, requires_action=bool(actions), deadline=deadline, is_overdue=overdue, is_new_lead=classification.is_new_lead, is_existing_client=classification.is_existing_client, attention_score=min(score, 100), priority=priority_for(score), reasons=reasons)
