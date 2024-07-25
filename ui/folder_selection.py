from PySide6.QtWidgets import QWidget, QPushButton, QListView, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QLabel
from PySide6.QtCore import QStringListModel
from config import save_settings

class FolderSelectionFrame(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.label = QLabel("\u25cf Folders to Monitor")
        font = self.label.font()
        font.setBold(True)
        self.label.setFont(font)
        self.listView = QListView()
        self.listView.setFixedHeight(150)  # 원하는 높이로 설정
        self.buttonLayout = QHBoxLayout()
        self.selectButton = QPushButton("Select Folders")
        self.removeButton = QPushButton("Remove")
        self.selectButton.clicked.connect(self.select_folders)
        self.removeButton.clicked.connect(self.remove_selected_folders)
        self.buttonLayout.addWidget(self.selectButton)
        self.buttonLayout.addWidget(self.removeButton)
        layout.addWidget(self.label)
        layout.addWidget(self.listView)
        layout.addLayout(self.buttonLayout)
        self.setLayout(layout)
        self.update_listView()

    def select_folders(self):
        if self.app is None or not hasattr(self.app, 'monitored_folders'):
            QMessageBox.warning(self, "Error", "Application context is not properly set.")
            return
        folder = QFileDialog.getExistingDirectory(self, "Select Folders to Monitor", "", QFileDialog.Option.ShowDirsOnly)
        if folder:
            self.app.monitored_folders.append(folder)
            save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)
            self.update_listView()

    def remove_selected_folders(self):
        if self.app is None or not hasattr(self.app, 'monitored_folders'):
            QMessageBox.warning(self, "Error", "Application context is not properly set.")
            return
        selected = self.listView.selectedIndexes()
        for index in sorted([index.row() for index in selected], reverse=True):
            del self.app.monitored_folders[index]
        save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)
        self.update_listView()

    def update_listView(self):
        if self.app is None or not hasattr(self.app, 'monitored_folders'):
            QMessageBox.warning(self, "Error", "Application context is not properly set.")
            return
        model = QStringListModel(self.app.monitored_folders)
        self.listView.setModel(model)
