from PySide6.QtWidgets import QWidget, QPushButton, QListView, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QLabel, QGroupBox
from PySide6.QtCore import QStringListModel
from config import save_settings
import os

class FolderMonitorFrame(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Folder to Monitor GroupBox
        folder_groupbox = QGroupBox("Folder to Monitor")
        folder_layout = QHBoxLayout()

        # Target Folders
        target_layout = QVBoxLayout()
        self.target_label = QLabel("Target Folders")
        self.target_list = QListView()
        self.target_select_button = QPushButton("Select Folders")
        self.target_remove_button = QPushButton("Remove")
        self.target_button_layout = QHBoxLayout()
        self.target_button_layout.addWidget(self.target_select_button)
        self.target_button_layout.addWidget(self.target_remove_button)

        self.target_select_button.clicked.connect(self.select_target_folders)
        self.target_remove_button.clicked.connect(self.remove_target_folders)

        target_layout.addWidget(self.target_label)
        target_layout.addWidget(self.target_list)
        target_layout.addLayout(self.target_button_layout)

        # Exclude Folders
        exclude_layout = QVBoxLayout()
        self.exclude_label = QLabel("Exclude Folders")
        self.exclude_list = QListView()
        self.exclude_select_button = QPushButton("Select Folders")
        self.exclude_remove_button = QPushButton("Remove")
        self.exclude_button_layout = QHBoxLayout()
        self.exclude_button_layout.addWidget(self.exclude_select_button)
        self.exclude_button_layout.addWidget(self.exclude_remove_button)

        self.exclude_select_button.clicked.connect(self.select_exclude_folders)
        self.exclude_remove_button.clicked.connect(self.remove_exclude_folders)

        exclude_layout.addWidget(self.exclude_label)
        exclude_layout.addWidget(self.exclude_list)
        exclude_layout.addLayout(self.exclude_button_layout)

        folder_layout.addLayout(target_layout)
        folder_layout.addLayout(exclude_layout)
        folder_groupbox.setLayout(folder_layout)

        # Save to Folder GroupBox
        save_groupbox = QGroupBox("Save to Folder")
        save_layout = QVBoxLayout()
        self.save_folder_label = QLabel(self.app.dest_folder if self.app.dest_folder else "")
        self.save_button = QPushButton("Select Folder")
        self.save_button.clicked.connect(self.select_save_folder)
        self.save_button_layout = QHBoxLayout()
        self.save_button_layout.addWidget(self.save_button)

        save_layout.addWidget(self.save_folder_label)
        save_layout.addLayout(self.save_button_layout)
        save_groupbox.setLayout(save_layout)

        layout.addWidget(folder_groupbox)
        layout.addWidget(save_groupbox)
        self.setLayout(layout)
        self.update_target_list()
        self.update_exclude_list()

    def select_save_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder", "", QFileDialog.Option.ShowDirsOnly)
        if folder:
            self.app.dest_folder = os.path.normpath(folder)  # 경로를 정규화하여 운영 체제에 맞게 표시
            self.save_folder_label.setText(self.app.dest_folder)
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

    def select_target_folders(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folders to Monitor", "", QFileDialog.Option.ShowDirsOnly)
        if folder:
            self.app.monitored_folders.append(os.path.normpath(folder))  # 경로를 정규화하여 운영 체제에 맞게 표시
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
            self.update_target_list()

    def remove_target_folders(self):
        selected = self.target_list.selectedIndexes()
        for index in sorted([index.row() for index in selected], reverse=True):
            del self.app.monitored_folders[index]
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
        self.update_target_list()

    def update_target_list(self):
        filtered_folders = [folder for folder in self.app.monitored_folders if folder != self.app.base_date_folder and not folder.startswith(os.path.join(self.app.dest_folder, 'wf_info'))]
        model = QStringListModel(filtered_folders)
        self.target_list.setModel(model)

    def select_exclude_folders(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folders to Exclude from Monitoring", "", QFileDialog.Option.ShowDirsOnly)
        if folder:
            self.app.exclude_folders.append(os.path.normpath(folder))  # 경로를 정규화하여 운영 체제에 맞게 표시
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
            self.update_exclude_list()

    def remove_exclude_folders(self):
        selected = self.exclude_list.selectedIndexes()
        for index in sorted([index.row() for index in selected], reverse=True):
            del self.app.exclude_folders[index]
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
        self.update_exclude_list()

    def update_exclude_list(self):
        model = QStringListModel(self.app.exclude_folders)
        self.exclude_list.setModel(model)

    def set_controls_enabled(self, enabled):
        """Enable or disable controls for folder monitoring."""
        self.target_list.setEnabled(enabled)
        self.target_select_button.setEnabled(enabled)
        self.target_remove_button.setEnabled(enabled)
        self.exclude_list.setEnabled(enabled)
        self.exclude_select_button.setEnabled(enabled)
        self.exclude_remove_button.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
