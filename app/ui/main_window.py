from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton, QSplitter, QVBoxLayout, QWidget
from .dashboard import Dashboard
from .email_detail import EmailDetail
from .settings import Settings


class MainWindow(QMainWindow):
    def __init__(self, analyses=None, on_connect=None, on_sync=None, config=None):
        super().__init__()
        self.setWindowTitle("Attention Inbox")
        self.resize(1100, 700)
        self.on_connect = on_connect
        self.on_sync = on_sync
        self.config = config if config is not None else {"days": 7, "profile": "contractor"}
        self.dashboard = Dashboard(analyses)
        self.detail = EmailDetail()

        topbar = QHBoxLayout()
        brand = QLabel("Attention Inbox")
        brand.setObjectName("brand")
        self.account_status = QLabel("Not connected")
        self.account_status.setObjectName("status")
        connect = QPushButton("Connect Gmail")
        connect.clicked.connect(self._connect)
        sync = QPushButton("Sync now")
        sync.clicked.connect(self._sync)
        settings = QPushButton("Settings")
        settings.clicked.connect(self._show_settings)
        topbar.addWidget(brand)
        topbar.addStretch()
        topbar.addWidget(self.account_status)
        topbar.addWidget(connect)
        topbar.addWidget(sync)
        topbar.addWidget(settings)

        splitter = QSplitter()
        splitter.addWidget(self.dashboard)
        splitter.addWidget(self.detail)
        splitter.setSizes([430, 670])
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.addLayout(topbar)
        page_layout.addWidget(splitter)
        self.setCentralWidget(page)
        self.dashboard.thread_selected.connect(self.detail.show_analysis)
        if analyses:
            self.dashboard.list.setCurrentRow(0)

    def _connect(self):
        if not self.on_connect:
            self.statusBar().showMessage("Gmail connection is not configured", 5000)
            return
        try:
            self.on_connect()
            self.account_status.setText("Gmail connected")
            self.statusBar().showMessage("Gmail connected", 5000)
        except Exception as error:
            QMessageBox.critical(self, "Connection failed", str(error))

    def _sync(self):
        if not self.on_sync:
            self.statusBar().showMessage("Connect Gmail before syncing", 5000)
            return
        try:
            analyses = self.on_sync()
            self.dashboard.refresh(analyses)
            if analyses:
                self.dashboard.list.setCurrentRow(0)
            self.statusBar().showMessage(f"Synced {len(analyses)} threads", 5000)
        except Exception as error:
            QMessageBox.critical(self, "Sync failed", str(error))

    def _show_settings(self):
        settings = Settings(on_connect=self._connect, on_sync=self._sync, parent=self)
        settings.days.setValue(self.config["days"])
        settings.profile.setCurrentText("Real estate" if self.config["profile"] == "real_estate" else "Contractor")
        if settings.exec():
            self.config["days"] = settings.days.value()
            self.config["profile"] = "real_estate" if settings.profile.currentText() == "Real estate" else "contractor"
            self.statusBar().showMessage("Settings saved", 3000)
