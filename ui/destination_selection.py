from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox
from config import save_settings

class DestinationSelectionFrame(QWidget):
    def __init__(self, parent=None, app_context=None):
        super().__init__(parent)
        self.app_context = app_context
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.label = QLabel("\u25cf Save to Folder")
        font = self.label.font()
        font.setBold(True)
        self.label.setFont(font)
        self.pathLabel = QLabel(self.app_context.dest_folder if self.app_context.dest_folder else "No folder selected")
        self.buttonLayout = QHBoxLayout()
        self.selectButton = QPushButton("Select Folder")
        self.selectButton.clicked.connect(self.select_destination_folder)
        self.buttonLayout.addWidget(self.selectButton)
        layout.addWidget(self.label)
        layout.addWidget(self.pathLabel)
        layout.addLayout(self.buttonLayout)
        self.setLayout(layout)

    def select_destination_folder(self):
        if self.app_context is None or not hasattr(self.app_context, 'dest_folder') or not hasattr(self.app_context, 'regex_folders'):
            QMessageBox.warning(self, "Error", "Application context is not properly set.")
            return
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder", "", QFileDialog.Option.ShowDirsOnly)
        if folder:
            self.app_context.dest_folder = folder
            self.pathLabel.setText(folder)
            save_settings(self.app_context.monitored_folders, self.app_context.dest_folder, self.app_context.regex_folders, self.app_context.exclude_folders, self.app_context.base_date_folder, self.app_context.target_compare_folders)
