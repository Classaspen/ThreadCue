import argparse
from datetime import datetime, timedelta, timezone
from PySide6.QtWidgets import QApplication, QFileDialog
from app.analysis.attention import analyze_thread
from app.analysis.classifier import load_rules
from app.db.database import create_database, session_factory
from app.db.repository import Repository
from app.domain.email import EmailMessage
from app.providers.gmail import GmailProvider
from app.services.analysis_service import AnalysisService
from app.services.sync_service import SyncService
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
    provider = GmailProvider()
    sync_service = None
    config = {"days": 7, "profile": "contractor"}

    def connect_gmail():
        nonlocal sync_service
        credentials_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select Google OAuth client file",
            "",
            "JSON files (*.json)",
        )
        if not credentials_path:
            raise RuntimeError("Gmail connection cancelled")
        provider.credentials_path = credentials_path
        provider.authenticate()
        engine = create_database()
        repository = Repository(session_factory(engine)())
        sync_service = SyncService(provider, repository, AnalysisService(load_rules(f"profiles/{config['profile']}.yaml")))

    def sync_gmail():
        if sync_service is None:
            raise RuntimeError("Connect Gmail before syncing")
        sync_service.analyzer.rules = load_rules(f"profiles/{config['profile']}.yaml")
        return sync_service.sync(days=config["days"])

    app = QApplication([])
    app.setStyleSheet("QMainWindow { background: #f4f1ea; } QWidget { color: #17324d; font-family: Segoe UI; font-size: 14px; } QLabel#brand { color: #ef8354; font-size: 22px; font-weight: 700; } QLabel#pageTitle { color: #17324d; font-size: 28px; font-weight: 700; padding-top: 8px; } QLabel#detailTitle { color: #17324d; font-size: 22px; font-weight: 700; } QLabel#status { color: #47756d; padding: 8px; } QPushButton { background: #17324d; color: white; border: 0; border-radius: 6px; padding: 9px 14px; } QPushButton:hover { background: #245473; } QComboBox, QSpinBox { background: white; border: 1px solid #d8d1c4; border-radius: 5px; padding: 7px; } QListWidget { background: #fffdf8; border: 1px solid #d8d1c4; border-radius: 6px; padding: 8px; } QListWidget::item { padding: 14px 8px; } QListWidget::item:selected { background: #dcefe9; color: #17324d; }")
    window = MainWindow(analyses, on_connect=None if args.demo else connect_gmail, on_sync=None if args.demo else sync_gmail, config=config)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
