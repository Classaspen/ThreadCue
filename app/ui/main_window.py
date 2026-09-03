from PySide6.QtWidgets import QMainWindow, QSplitter
from .dashboard import Dashboard
from .email_detail import EmailDetail


class MainWindow(QMainWindow):
    def __init__(self, analyses=None):
        super().__init__()
        self.setWindowTitle("Attention Inbox")
        self.resize(1100, 700)
        self.dashboard = Dashboard(analyses)
        self.detail = EmailDetail()
        splitter = QSplitter()
        splitter.addWidget(self.dashboard)
        splitter.addWidget(self.detail)
        splitter.setSizes([430, 670])
        self.setCentralWidget(splitter)
        self.dashboard.thread_selected.connect(self.detail.show_analysis)
        if analyses:
            self.dashboard.list.setCurrentRow(0)
