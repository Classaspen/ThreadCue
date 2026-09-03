from PySide6.QtWidgets import QFormLayout, QLabel, QPushButton, QSpinBox, QWidget


class Settings(QWidget):
    def __init__(self, on_connect=None):
        super().__init__()
        layout = QFormLayout(self)
        self.days = QSpinBox()
        self.days.setRange(1, 30)
        self.days.setValue(7)
        connect = QPushButton("Connect Gmail")
        connect.clicked.connect(on_connect or (lambda: None))
        layout.addRow("Sync window (days)", self.days)
        layout.addRow("Account", connect)
        layout.addRow("Privacy", QLabel("Read-only. Data stays on this computer."))
