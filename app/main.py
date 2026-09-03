import argparse
from datetime import datetime, timedelta, timezone
from PySide6.QtWidgets import QApplication
from app.analysis.attention import analyze_thread
from app.domain.email import EmailMessage
from app.ui.main_window import MainWindow


def demo_messages():
    now = datetime.now(timezone.utc)
    return [
        EmailMessage(id="demo-1", thread_id="thread-1", subject="Quote for kitchen renovation", sender="customer@example.com", recipients=["me@example.com"], body="Could you send a quote by Friday?", received_at=now - timedelta(hours=31)),
        EmailMessage(id="demo-2", thread_id="thread-2", subject="Invoice follow-up", sender="client@example.com", recipients=["me@example.com"], body="Please confirm payment for invoice 104.", received_at=now - timedelta(hours=10)),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Open with local sample data")
    args = parser.parse_args()
    messages = demo_messages() if args.demo else []
    analyses = [analyze_thread([message]) for message in messages]
    app = QApplication([])
    app.setStyleSheet("QMainWindow { background: #f4f1ea; } QLabel { color: #17324d; font-size: 15px; } QListWidget { background: #fffdf8; border: 1px solid #d8d1c4; padding: 8px; } QListWidget::item { padding: 14px 8px; } QListWidget::item:selected { background: #dcefe9; color: #17324d; }")
    window = MainWindow(analyses)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
