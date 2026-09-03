from PySide6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel, QPushButton, QSpinBox


class Settings(QDialog):
    def __init__(self, on_connect=None, on_sync=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(360)
        layout = QFormLayout(self)
        self.days = QSpinBox()
        self.days.setRange(1, 30)
        self.days.setValue(7)
        self.profile = QComboBox()
        self.profile.addItems(["Contractor", "Real estate"])
        connect = QPushButton("Connect Gmail")
        connect.clicked.connect(on_connect or (lambda: None))
        sync = QPushButton("Sync now")
        sync.clicked.connect(on_sync or (lambda: None))
        layout.addRow("Industry", self.profile)
        layout.addRow("Sync window (days)", self.days)
        layout.addRow("Account", connect)
        layout.addRow("Mailbox", sync)
        layout.addRow("Privacy", QLabel("Read-only. Data stays on this computer."))
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
