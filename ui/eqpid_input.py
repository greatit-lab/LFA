from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

class EqpidInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter EQPID")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("Please enter the EQPID:")
        self.eqpid_input = QLineEdit()

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        layout.addWidget(self.label)
        layout.addWidget(self.eqpid_input)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def get_eqpid(self):
        return self.eqpid_input.text()
