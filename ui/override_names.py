from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QListView, QFileDialog, QMessageBox
from PySide6.QtCore import QStringListModel
from config import save_settings

class OverrideNamesFrame(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Base Date File Path Section
        self.base_date_label = QLabel("\u25cf Base Date File Path (Date)")
        font = self.base_date_label.font()
        font.setBold(True)
        self.base_date_label.setFont(font)
        self.base_date_combo = QComboBox()
        self.base_date_combo.addItem("Unselected")  # 초기값 설정
        self.base_date_clear_button = QPushButton("Clear")
        base_date_layout = QHBoxLayout()
        base_date_layout.addWidget(self.base_date_combo)
        base_date_layout.addWidget(self.base_date_clear_button)

        self.base_date_clear_button.clicked.connect(self.clear_base_date)

        # Target Compare File Paths Section
        self.target_compare_label = QLabel("\u25cf Target compare file paths (Slot)")
        font = self.target_compare_label.font()
        font.setBold(True)
        self.target_compare_label.setFont(font)
        self.target_compare_list = QListView()
        self.target_compare_add_button = QPushButton("Select Folders")
        self.target_compare_remove_button = QPushButton("Remove")
        target_compare_button_layout = QVBoxLayout()
        target_compare_button_layout.addWidget(self.target_compare_add_button)
        target_compare_button_layout.addWidget(self.target_compare_remove_button)

        self.target_compare_add_button.clicked.connect(self.add_target_compare_path)
        self.target_compare_remove_button.clicked.connect(self.remove_target_compare_path)

        target_compare_layout = QHBoxLayout()
        target_compare_layout.addWidget(self.target_compare_list)
        target_compare_layout.addLayout(target_compare_button_layout)

        layout.addWidget(self.base_date_label)
        layout.addLayout(base_date_layout)
        layout.addWidget(self.target_compare_label)
        layout.addLayout(target_compare_layout)
        self.setLayout(layout)
        self.update_base_date_combo()
        self.update_target_compare_list()

    def update_base_date_combo(self):
        self.base_date_combo.clear()
        self.base_date_combo.addItem("Unselected")  # 기본값 설정
        self.base_date_combo.addItems(self.app.regex_folders.values())

    def clear_base_date(self):
        self.base_date_combo.setCurrentIndex(0)  # 콤보박스를 "Unselected"로 되돌림

    def add_target_compare_path(self):
        save_to_folder = self.app.dest_folder
        folder = QFileDialog.getExistingDirectory(self, "Select Target Compare Folder", save_to_folder, QFileDialog.Option.ShowDirsOnly)
        if folder:
            if not folder.startswith(save_to_folder):
                QMessageBox.warning(self, "Warning", f"Please select a folder within {save_to_folder}.")
                return
            self.app.target_compare_folders.append(folder)
            save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)
            if self.app.logger:
                self.app.logger.log_event("Target Compare Folder Added", folder)
                self.app.logger.log_debug(f"Target compare folder added: {folder}")
            self.update_target_compare_list()

    def remove_target_compare_path(self):
        selected = self.target_compare_list.selectedIndexes()
        for index in sorted(selected, key=lambda idx: idx.row(), reverse=True):
            folder = self.app.target_compare_folders[index.row()]
            del self.app.target_compare_folders[index.row()]
            if self.app.logger:
                self.app.logger.log_event("Target Compare Folder Removed", folder)
                self.app.logger.log_debug(f"Target compare folder removed: {folder}")
        save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)
        self.update_target_compare_list()

    def update_target_compare_list(self):
        model = QStringListModel(self.app.target_compare_folders)
        self.target_compare_list.setModel(model)

    def set_controls_enabled(self, enabled):
        """Enable or disable controls for override names."""
        self.base_date_combo.setEnabled(enabled)
        self.base_date_clear_button.setEnabled(enabled)
        self.target_compare_list.setEnabled(enabled)
        self.target_compare_add_button.setEnabled(enabled)
        self.target_compare_remove_button.setEnabled(enabled)
