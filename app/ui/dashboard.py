from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget


class Dashboard(QWidget):
    thread_selected = Signal(object)

    def __init__(self, analyses=None):
        super().__init__()
        self.analyses = analyses or []
        self.filtered_analyses = []
        self.summary = QLabel()
        self.filter = QComboBox()
        self.filter.addItems(["All attention", "Critical", "High", "Medium", "Low"])
        self.filter.currentTextChanged.connect(self._apply_filter)
        self.list = QListWidget()
        self.list.setMinimumWidth(430)
        self.list.currentRowChanged.connect(self._select)
        layout = QVBoxLayout(self)
        heading = QLabel("Your attention inbox")
        heading.setObjectName("pageTitle")
        layout.addWidget(heading)
        layout.addWidget(self.summary)
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Show"))
        toolbar.addWidget(self.filter)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        layout.addWidget(self.list)
        self.refresh(self.analyses)

    def refresh(self, analyses):
        self.analyses = analyses
        critical = sum(item.priority == "CRITICAL" for item in analyses)
        high = sum(item.priority == "HIGH" for item in analyses)
        self.summary.setText(f"{len(analyses)} threads need review  |  {critical} critical  |  {high} high")
        self._apply_filter(self.filter.currentText())

    def _apply_filter(self, selected):
        priority = selected.upper() if selected != "All attention" else None
        self.filtered_analyses = [item for item in self.analyses if priority is None or item.priority == priority]
        self.list.clear()
        if not self.filtered_analyses:
            empty = QListWidgetItem("Nothing needs your attention here")
            empty.setFlags(Qt.ItemIsEnabled)
            self.list.addItem(empty)
        for analysis in self.filtered_analyses:
            item = QListWidgetItem(f"{analysis.priority}   {analysis.attention_score:>3}   {analysis.subject}")
            item.setData(256, analysis)
            self.list.addItem(item)

    def _select(self, row):
        if row >= 0:
            analysis = self.list.item(row).data(256)
            if analysis is not None:
                self.thread_selected.emit(analysis)
