from datetime import datetime
from app.analysis.deadline_detector import detect_deadline


def test_detects_explicit_date():
    result = detect_deadline("Please reply by September 10", datetime(2026, 9, 1))
    assert result is not None
    assert result.day == 10
