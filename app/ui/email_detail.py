from PySide6.QtWidgets import QLabel, QListWidget, QVBoxLayout, QWidget


class EmailDetail(QWidget):
    def __init__(self):
        super().__init__()
        self.title = QLabel("Select a thread")
        self.meta = QLabel("")
        self.reasons = QListWidget()
        layout = QVBoxLayout(self)
        layout.addWidget(self.title)
        layout.addWidget(self.meta)
        layout.addWidget(self.reasons)

    def show_analysis(self, analysis):
        self.title.setText(analysis.subject)
        self.meta.setText(f"{analysis.priority}  |  {analysis.state.value}  |  score {analysis.attention_score}")
        self.reasons.clear()
        for reason in analysis.reasons:
            self.reasons.addItem(reason)
