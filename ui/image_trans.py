from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QFileDialog, QMessageBox, QGroupBox
from config import save_settings
import os

class ImageTransFrame(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Set a Condition GroupBox
        condition_group = QGroupBox("Set a Condition")
        condition_layout = QVBoxLayout()

        # Target Image Folder Section
        target_image_folder_layout = QHBoxLayout()
        self.target_image_folder_label = QLabel("Target Image Folder")
        self.target_image_folder_combo = QComboBox()
        self.target_image_folder_combo.addItem("Unselected")
        self.target_image_folder_combo.addItems(self.app.regex_folders.values())
        self.target_image_folder_combo.setCurrentText(self.app.target_image_folder)
        self.target_image_folder_combo.currentTextChanged.connect(self.update_target_image_folder)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_target_image_folder)

        target_image_folder_layout.addWidget(self.target_image_folder_label)
        target_image_folder_layout.addWidget(self.target_image_folder_combo)
        target_image_folder_layout.addWidget(self.clear_button)

        # Wait Time Section
        wait_time_layout = QHBoxLayout()
        self.wait_time_label = QLabel("Wait Time")
        self.wait_time_combo = QComboBox()
        wait_times = ["60", "120", "180", "240", "300", "600"]
        self.wait_time_combo.addItems(wait_times)
        self.wait_time_combo.setCurrentText(self.app.wait_time)
        self.wait_time_combo.currentTextChanged.connect(self.update_wait_time)

        wait_time_layout.addWidget(self.wait_time_label)
        wait_time_layout.addWidget(self.wait_time_combo)

        condition_layout.addLayout(target_image_folder_layout)
        condition_layout.addLayout(wait_time_layout)
        condition_group.setLayout(condition_layout)

        # Image Save Folder Section
        save_folder_group = QGroupBox("Image Save Folder")
        save_folder_layout = QHBoxLayout()
        self.image_save_folder_path = QLabel(os.path.normpath(self.app.image_save_folder))
        self.image_save_folder_button = QPushButton("Select Folder")
        self.image_save_folder_button.clicked.connect(self.select_image_save_folder)

        save_folder_layout.addWidget(self.image_save_folder_path)
        save_folder_layout.addWidget(self.image_save_folder_button)
        save_folder_group.setLayout(save_folder_layout)

        # Add all components to the main layout
        main_layout.addWidget(condition_group)
        main_layout.addWidget(save_folder_group)
        
        self.setLayout(main_layout)

    def clear_target_image_folder(self):
        self.target_image_folder_combo.setCurrentText("Unselected")

    def select_image_save_folder(self):
        save_to_folder = self.app.dest_folder
        folder = QFileDialog.getExistingDirectory(self, "Select Image Save Folder", save_to_folder, QFileDialog.Option.ShowDirsOnly)
        if folder:
            normalized_folder = os.path.normpath(folder)  # 경로를 정규화하여 운영 체제에 맞게 표시
            if not normalized_folder.startswith(os.path.abspath(save_to_folder)):
                QMessageBox.warning(self, "Warning", f"Please select a folder within {save_to_folder}.")
                return
            self.image_save_folder_path.setText(normalized_folder)
            self.app.image_save_folder = normalized_folder
            self.update_settings()

    def update_target_image_folder(self, text):
        self.app.target_image_folder = text
        self.update_settings()

    def update_wait_time(self, text):
        self.app.wait_time = text
        self.update_settings()

    def update_settings(self):
        save_settings(
            self.app.monitored_folders,
            self.app.dest_folder,
            self.app.regex_folders,
            self.app.exclude_folders,
            self.app.base_date_folder,
            self.app.target_compare_folders,
            self.app.target_image_folder,
            self.app.wait_time,
            self.app.image_save_folder,
            self.app.wafer_flat_data_path,
            self.app.prealign_data_path,
            self.app.image_data_path
        )

    def set_controls_enabled(self, enabled):
        """Enable or disable controls for image trans."""
        self.target_image_folder_combo.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)
        self.wait_time_combo.setEnabled(enabled)
        self.image_save_folder_button.setEnabled(enabled)
