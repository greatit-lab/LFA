from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListView, QPushButton, QHBoxLayout, QComboBox, QInputDialog, QMessageBox, QFileDialog
from PySide6.QtCore import QStringListModel
from config import save_settings

class SeparationFrame(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Regex Categorization Section
        self.regex_label = QLabel("\u25cf Regex Categorization")
        font = self.regex_label.font()
        font.setBold(True)
        self.regex_label.setFont(font)
        self.regex_list = QListView()
        self.regex_add_button = QPushButton("Add Regex")
        self.regex_edit_button = QPushButton("Edit Regex")
        self.regex_remove_button = QPushButton("Remove")
        self.regex_button_layout = QVBoxLayout()
        self.regex_button_layout.addWidget(self.regex_add_button)
        self.regex_button_layout.addWidget(self.regex_edit_button)
        self.regex_button_layout.addWidget(self.regex_remove_button)

        self.regex_add_button.clicked.connect(self.add_regex)
        self.regex_edit_button.clicked.connect(self.edit_regex)
        self.regex_remove_button.clicked.connect(self.remove_regex)

        regex_layout = QHBoxLayout()
        regex_layout.addWidget(self.regex_list)
        regex_layout.addLayout(self.regex_button_layout)

        # Rename a Date Section
        self.rename_label = QLabel("\u25cf Rename a Date")
        font = self.rename_label.font()
        font.setBold(True)
        self.rename_label.setFont(font)
        self.rename_combo = QComboBox()
        self.rename_combo.addItem("Unselected")  # 초기값 설정
        self.rename_clear_button = QPushButton("Clear")
        rename_layout = QHBoxLayout()
        rename_layout.addWidget(self.rename_combo)
        rename_layout.addWidget(self.rename_clear_button)

        self.rename_clear_button.clicked.connect(self.clear_rename)

        layout.addWidget(self.regex_label)
        layout.addLayout(regex_layout)
        layout.addWidget(self.rename_label)
        layout.addLayout(rename_layout)
        self.setLayout(layout)
        self.update_regex_list()

    def add_regex(self):
        pattern, ok = QInputDialog.getText(self, "Input", "Enter regex pattern:")
        if ok and pattern:
            subfolder = self.select_subfolder()
            if subfolder:
                self.app.regex_folders[pattern] = subfolder
                save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)
                self.update_regex_list()

    def edit_regex(self):
        selected = self.regex_list.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, "Warning", "No pattern selected.")
            return
        selected_index = selected[0].row()
        pattern = list(self.app.regex_folders.keys())[selected_index]
        subfolder = self.app.regex_folders[pattern]
        new_pattern, ok = QInputDialog.getText(self, "Input", "Edit regex pattern:", text=pattern)
        if ok and new_pattern:
            new_subfolder = self.select_subfolder(default_path=subfolder)
            if new_subfolder:
                del self.app.regex_folders[pattern]
                self.app.regex_folders[new_pattern] = new_subfolder
                save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)
                self.update_regex_list()

    def remove_regex(self):
        selected = self.regex_list.selectedIndexes()
        for index in sorted([index.row() for index in selected], reverse=True):
            pattern = list(self.app.regex_folders.keys())[index]
            del self.app.regex_folders[pattern]
        save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)
        self.update_regex_list()

    def update_regex_list(self):
        model = QStringListModel([f"{pattern} -> {subfolder}" for pattern, subfolder in self.app.regex_folders.items()])
        self.regex_list.setModel(model)
        self.rename_combo.clear()
        self.rename_combo.addItem("Unselected")  # 기본값 설정
        self.rename_combo.addItems(self.app.regex_folders.values())

    def clear_rename(self):
        self.rename_combo.setCurrentIndex(0)  # 콤보박스를 "Unselected"로 되돌림

    def select_subfolder(self, default_path=''):
        folder = QFileDialog.getExistingDirectory(self, "Select Subfolder", default_path, QFileDialog.Option.ShowDirsOnly)
        return folder if folder else None
