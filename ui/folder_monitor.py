from PySide6.QtWidgets import QWidget, QPushButton, QListView, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QLabel, QGroupBox
from PySide6.QtCore import QStringListModel
from config import save_settings
import os

class FolderMonitorFrame(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app  # 앱의 컨텍스트를 저장합니다.
        self.initUI()  # UI를 초기화합니다.

    def initUI(self):
        # UI를 설정하는 메서드입니다.
        layout = QVBoxLayout()

        # Folder to Monitor GroupBox
        # 모니터링할 폴더를 선택하는 그룹박스를 만듭니다.
        folder_groupbox = QGroupBox("Folder to Monitor")
        folder_layout = QHBoxLayout()

        # Target Folders
        # 모니터링 대상 폴더를 관리하는 섹션입니다.
        target_layout = QVBoxLayout()
        self.target_label = QLabel("Target Folders")
        self.target_list = QListView()  # 대상 폴더 목록을 보여줍니다.
        self.target_select_button = QPushButton("Select Folders")  # 폴더 선택 버튼
        self.target_remove_button = QPushButton("Remove")  # 폴더 제거 버튼
        self.target_button_layout = QHBoxLayout()
        self.target_button_layout.addWidget(self.target_select_button)
        self.target_button_layout.addWidget(self.target_remove_button)

        # 버튼 클릭 시 호출되는 메서드를 연결합니다.
        self.target_select_button.clicked.connect(self.select_target_folders)
        self.target_remove_button.clicked.connect(self.remove_target_folders)

        target_layout.addWidget(self.target_label)
        target_layout.addWidget(self.target_list)
        target_layout.addLayout(self.target_button_layout)

        # Exclude Folders
        # 모니터링에서 제외할 폴더를 관리하는 섹션입니다.
        exclude_layout = QVBoxLayout()
        self.exclude_label = QLabel("Exclude Folders")
        self.exclude_list = QListView()  # 제외할 폴더 목록을 보여줍니다.
        self.exclude_select_button = QPushButton("Select Folders")  # 폴더 선택 버튼
        self.exclude_remove_button = QPushButton("Remove")  # 폴더 제거 버튼
        self.exclude_button_layout = QHBoxLayout()
        self.exclude_button_layout.addWidget(self.exclude_select_button)
        self.exclude_button_layout.addWidget(self.exclude_remove_button)

        # 버튼 클릭 시 호출되는 메서드를 연결합니다.
        self.exclude_select_button.clicked.connect(self.select_exclude_folders)
        self.exclude_remove_button.clicked.connect(self.remove_exclude_folders)

        exclude_layout.addWidget(self.exclude_label)
        exclude_layout.addWidget(self.exclude_list)
        exclude_layout.addLayout(self.exclude_button_layout)

        # 대상 폴더 섹션과 제외할 폴더 섹션을 레이아웃에 추가합니다.
        folder_layout.addLayout(target_layout)
        folder_layout.addLayout(exclude_layout)
        folder_groupbox.setLayout(folder_layout)

        # Save to Folder GroupBox
        # 저장할 폴더를 선택하는 그룹박스를 만듭니다.
        save_groupbox = QGroupBox("Save to Folder")
        save_layout = QVBoxLayout()
        self.save_folder_label = QLabel(self.app.dest_folder if self.app.dest_folder else "")   # type: ignore
        self.save_button = QPushButton("Select Folder")  # 폴더 선택 버튼
        self.save_button.clicked.connect(self.select_save_folder)
        self.save_button_layout = QHBoxLayout()
        self.save_button_layout.addWidget(self.save_button)

        save_layout.addWidget(self.save_folder_label)
        save_layout.addLayout(self.save_button_layout)
        save_groupbox.setLayout(save_layout)

        # 레이아웃에 그룹박스를 추가합니다.
        layout.addWidget(folder_groupbox)
        layout.addWidget(save_groupbox)
        self.setLayout(layout)

        # 초기 대상 폴더 및 제외 폴더 목록을 업데이트합니다.
        self.update_target_list()
        self.update_exclude_list()

    def select_save_folder(self):
        # 저장할 폴더를 선택하고 경로를 설정하는 메서드입니다.
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder", "", QFileDialog.Option.ShowDirsOnly)
        if folder:
            # 선택한 폴더 경로를 저장하고 UI에 표시합니다.
            self.app.dest_folder = os.path.normpath(folder)     # type: ignore  # 경로를 정규화하여 운영 체제에 맞게 표시
            self.save_folder_label.setText(self.app.dest_folder)    # type: ignore
            # 설정을 저장합니다.
            save_settings(self.app.monitored_folders,self.app.dest_folder,self.app.regex_folders,self.app.exclude_folders,self.app.base_date_folder,self.app.target_compare_folders,self.app.target_image_folder,self.app.wait_time,self.app.image_save_folder,self.app.wafer_flat_data_path,self.app.prealign_data_path,self.app.image_data_path)  # type: ignore

    def select_target_folders(self):
        # 모니터링할 폴더를 선택하는 메서드입니다.
        folder = QFileDialog.getExistingDirectory(self, "Select Folders to Monitor", "", QFileDialog.Option.ShowDirsOnly)
        if folder:
            # 선택한 폴더를 목록에 추가하고 설정을 저장합니다.
            self.app.monitored_folders.append(os.path.normpath(folder))     # type: ignore  # 경로를 정규화하여 운영 체제에 맞게 표시
            save_settings(self.app.monitored_folders,self.app.dest_folder,self.app.regex_folders,self.app.exclude_folders,self.app.base_date_folder,self.app.target_compare_folders,self.app.target_image_folder,self.app.wait_time,self.app.image_save_folder,self.app.wafer_flat_data_path,self.app.prealign_data_path,self.app.image_data_path)  # type: ignore
            # 목록을 업데이트합니다.
            self.update_target_list()

    def remove_target_folders(self):
        # 선택된 폴더를 모니터링 대상에서 제거하는 메서드입니다.
        selected = self.target_list.selectedIndexes()
        for index in sorted([index.row() for index in selected], reverse=True):
            del self.app.monitored_folders[index]   # type: ignore
        # 설정을 저장하고 목록을 업데이트합니다.
        save_settings(self.app.monitored_folders,self.app.dest_folder,self.app.regex_folders,self.app.exclude_folders,self.app.base_date_folder,self.app.target_compare_folders,self.app.target_image_folder,self.app.wait_time,self.app.image_save_folder,self.app.wafer_flat_data_path,self.app.prealign_data_path,self.app.image_data_path)  # type: ignore
        self.update_target_list()

    def update_target_list(self):
        # 모니터링할 폴더 목록을 UI에 업데이트하는 메서드입니다.
        filtered_folders = [folder for folder in self.app.monitored_folders if folder != self.app.base_date_folder and not folder.startswith(os.path.join(self.app.dest_folder, 'wf_info'))]    # type: ignore
        model = QStringListModel(filtered_folders)
        self.target_list.setModel(model)

    def select_exclude_folders(self):
        # 모니터링에서 제외할 폴더를 선택하는 메서드입니다.
        folder = QFileDialog.getExistingDirectory(self, "Select Folders to Exclude from Monitoring", "", QFileDialog.Option.ShowDirsOnly)
        if folder:
            # 선택한 폴더를 제외 목록에 추가하고 설정을 저장합니다.
            self.app.exclude_folders.append(os.path.normpath(folder))   # type: ignore  # 경로를 정규화하여 운영 체제에 맞게 표시
            save_settings(self.app.monitored_folders,self.app.dest_folder,self.app.regex_folders,self.app.exclude_folders,self.app.base_date_folder,self.app.target_compare_folders,self.app.target_image_folder,self.app.wait_time,self.app.image_save_folder,self.app.wafer_flat_data_path,self.app.prealign_data_path,self.app.image_data_path)  # type: ignore
            # 목록을 업데이트합니다.
            self.update_exclude_list()

    def remove_exclude_folders(self):
        # 제외 폴더 목록에서 선택된 폴더를 제거하는 메서드입니다.
        selected = self.exclude_list.selectedIndexes()
        for index in sorted([index.row() for index in selected], reverse=True):
            del self.app.exclude_folders[index]     # type: ignore
        # 설정을 저장하고 목록을 업데이트합니다.
        save_settings(self.app.monitored_folders,self.app.dest_folder,self.app.regex_folders,self.app.exclude_folders,self.app.base_date_folder,self.app.target_compare_folders,self.app.target_image_folder,self.app.wait_time,self.app.image_save_folder,self.app.wafer_flat_data_path,self.app.prealign_data_path,self.app.image_data_path)  # type: ignore
        self.update_exclude_list()

    def update_exclude_list(self):
        # 제외할 폴더 목록을 UI에 업데이트하는 메서드입니다.
        model = QStringListModel(self.app.exclude_folders)      # type: ignore
        self.exclude_list.setModel(model)

    def set_controls_enabled(self, enabled):
        """Enable or disable controls for folder monitoring."""
        # 폴더 모니터링에 필요한 UI 요소들을 활성화 또는 비활성화합니다.
        self.target_list.setEnabled(enabled)
        self.target_select_button.setEnabled(enabled)
        self.target_remove_button.setEnabled(enabled)
        self.exclude_list.setEnabled(enabled)
        self.exclude_select_button.setEnabled(enabled)
        self.exclude_remove_button.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
