from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QLabel


class Dashboard(QWidget):
    thread_selected = Signal(object)

    def __init__(self, analyses=None):
        super().__init__()
        self.analyses = analyses or []
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._select)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("ATTENTION INBOX"))
        layout.addWidget(self.list)
        self.refresh(self.analyses)

    def refresh(self, analyses):
        self.analyses = analyses
        self.list.clear()
        for analysis in analyses:
            item = QListWidgetItem(f"{analysis.priority}  {analysis.attention_score:>3}  {analysis.subject}")
            item.setData(256, analysis)
            self.list.addItem(item)

    def _select(self, row):
        if row >= 0:
            self.thread_selected.emit(self.list.item(row).data(256))
