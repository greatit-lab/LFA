from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QFileDialog, QMessageBox, QGroupBox
from config import save_settings
import os

class ImageTransFrame(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app  # 애플리케이션 컨텍스트를 저장하여 설정에 접근할 수 있도록 합니다.
        self.initUI()  # UI를 초기화합니다.

    def initUI(self):
        main_layout = QVBoxLayout()  # 메인 레이아웃을 수직 레이아웃으로 설정합니다.

        # 조건 설정 그룹 박스
        condition_group = QGroupBox("Set a Condition")  # 조건을 설정하는 그룹 박스를 생성합니다.
        condition_layout = QVBoxLayout()  # 조건 레이아웃을 수직 레이아웃으로 설정합니다.

        # Target Image Folder 섹션
        target_image_folder_layout = QHBoxLayout()  # 타겟 이미지 폴더 섹션의 수평 레이아웃을 설정합니다.
        self.target_image_folder_label = QLabel("Target Image Folder")  # 타겟 이미지 폴더 레이블을 생성합니다.
        self.target_image_folder_combo = QComboBox()  # 타겟 이미지 폴더를 선택하는 콤보박스를 생성합니다.
        self.target_image_folder_combo.addItem("Unselected")  # 기본값으로 'Unselected'를 추가합니다.
        self.target_image_folder_combo.addItems(self.app.regex_folders.values())  # 설정에서 정규식 폴더 목록을 추가합니다.
        self.target_image_folder_combo.setCurrentText(self.app.target_image_folder)  # 현재 설정된 타겟 폴더를 선택합니다.
        self.target_image_folder_combo.currentTextChanged.connect(self.update_target_image_folder)  # 선택된 폴더가 변경되면 업데이트합니다.
        self.clear_button = QPushButton("Clear")  # 타겟 폴더 선택을 초기화할 수 있는 버튼을 생성합니다.
        self.clear_button.clicked.connect(self.clear_target_image_folder)  # 버튼 클릭 시 타겟 폴더를 초기화합니다.

        target_image_folder_layout.addWidget(self.target_image_folder_label)
        target_image_folder_layout.addWidget(self.target_image_folder_combo)
        target_image_folder_layout.addWidget(self.clear_button)

        # Wait Time 섹션
        wait_time_layout = QHBoxLayout()  # 대기 시간 섹션의 수평 레이아웃을 설정합니다.
        self.wait_time_label = QLabel("Wait Time")  # 대기 시간 레이블을 생성합니다.
        self.wait_time_combo = QComboBox()  # 대기 시간을 선택하는 콤보박스를 생성합니다.
        wait_times = ["60", "120", "180", "240", "300", "600"]  # 대기 시간을 선택할 수 있는 옵션을 추가합니다.
        self.wait_time_combo.addItems(wait_times)
        self.wait_time_combo.setCurrentText(self.app.wait_time)  # 현재 설정된 대기 시간을 선택합니다.
        self.wait_time_combo.currentTextChanged.connect(self.update_wait_time)  # 대기 시간이 변경되면 업데이트합니다.

        wait_time_layout.addWidget(self.wait_time_label)
        wait_time_layout.addWidget(self.wait_time_combo)

        condition_layout.addLayout(target_image_folder_layout)
        condition_layout.addLayout(wait_time_layout)
        condition_group.setLayout(condition_layout)

        # Image Save Folder 섹션
        save_folder_group = QGroupBox("Image Save Folder")  # 이미지 저장 폴더 그룹 박스를 생성합니다.
        save_folder_layout = QHBoxLayout()  # 이미지 저장 폴더 섹션의 수평 레이아웃을 설정합니다.
        self.image_save_folder_path = QLabel(os.path.normpath(self.app.image_save_folder))  # 현재 이미지 저장 폴더 경로를 표시합니다.
        self.image_save_folder_button = QPushButton("Select Folder")  # 폴더 선택 버튼을 생성합니다.
        self.image_save_folder_button.clicked.connect(self.select_image_save_folder)  # 버튼 클릭 시 폴더 선택을 수행합니다.

        save_folder_layout.addWidget(self.image_save_folder_path)
        save_folder_layout.addWidget(self.image_save_folder_button)
        save_folder_group.setLayout(save_folder_layout)

        # 모든 구성 요소를 메인 레이아웃에 추가합니다.
        main_layout.addWidget(condition_group)
        main_layout.addWidget(save_folder_group)
        
        self.setLayout(main_layout)

    def clear_target_image_folder(self):
        """타겟 이미지 폴더 선택을 초기화합니다."""
        self.target_image_folder_combo.setCurrentText("Unselected")

    def select_image_save_folder(self):
        """이미지를 저장할 폴더를 선택합니다."""
        save_to_folder = self.app.dest_folder
        folder = QFileDialog.getExistingDirectory(self, "Select Image Save Folder", save_to_folder, QFileDialog.Option.ShowDirsOnly)
        if folder:
            normalized_folder = os.path.normpath(folder)  # 선택된 경로를 정규화하여 운영 체제에 맞게 표시합니다.
            if not normalized_folder.startswith(os.path.abspath(save_to_folder)):
                QMessageBox.warning(self, "Warning", f"Please select a folder within {save_to_folder}.")
                return
            self.image_save_folder_path.setText(normalized_folder)
            self.app.image_save_folder = normalized_folder
            self.update_settings()

    def update_target_image_folder(self, text):
        """선택된 타겟 이미지 폴더를 업데이트합니다."""
        self.app.target_image_folder = text
        self.update_settings()

    def update_wait_time(self, text):
        """대기 시간을 업데이트합니다."""
        self.app.wait_time = text
        self.update_settings()

    def update_settings(self):
        """현재 설정을 저장합니다."""
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
        """이미지 변환에 대한 제어를 활성화 또는 비활성화합니다."""
        self.target_image_folder_combo.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)
        self.wait_time_combo.setEnabled(enabled)
        self.image_save_folder_button.setEnabled(enabled)
