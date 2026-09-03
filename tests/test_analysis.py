from datetime import datetime, timedelta, timezone
from app.analysis.attention import analyze_thread
from app.domain.email import EmailMessage


def message(body, outgoing=False, hours=0, thread="t1"):
    return EmailMessage(id=f"{thread}-{outgoing}-{hours}", thread_id=thread, subject="Quote request", sender="customer@example.com", recipients=["me@example.com"], body=body, received_at=datetime.now(timezone.utc) - timedelta(hours=hours), is_outgoing=outgoing)


def test_quote_request_waits_on_user_and_is_explainable():
    result = analyze_thread([message("Please send a quote for the work.", hours=49)])
    assert result.state.value == "QUOTE_REQUIRED"
    assert result.priority in {"HIGH", "CRITICAL"}
    assert any("Quote request" in reason for reason in result.reasons)


def test_outbound_message_waits_on_customer():
    result = analyze_thread([message("Please send the details", hours=4), message("I sent the details", outgoing=True, hours=2)])
    assert result.state.value == "WAITING_ON_CUSTOMER"
