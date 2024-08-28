from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QGroupBox
from config import save_settings

class UploadDataFrame(QWidget):
    def __init__(self, parent=None, app=None):
        # 초기화 메서드입니다. 부모 위젯과 앱 컨텍스트를 받아옵니다.
        super().__init__(parent)
        self.app = app  # 앱 컨텍스트를 저장합니다.
        self.initUI()  # UI를 초기화하는 메서드를 호출합니다.

    def initUI(self):
        # 메인 레이아웃을 설정합니다.
        main_layout = QVBoxLayout()

        # Database Uploading GroupBox 설정
        # 데이터베이스 업로드와 관련된 UI 요소들을 그룹화합니다.
        database_group = QGroupBox("Database Uploading")
        database_layout = QVBoxLayout()

        # Wafer Flat Data Path 섹션
        # 웨이퍼 플랫 데이터 경로를 선택하는 섹션입니다.
        wafer_flat_layout = QHBoxLayout()
        self.wafer_flat_label = QLabel("Wafer Flat Data Path")
        self.wafer_flat_combo = QComboBox()
        # 초기값으로 "Unselected"를 설정하고, 앱에서 설정한 경로들을 추가합니다.
        self.wafer_flat_combo.addItem("Unselected")
        self.wafer_flat_combo.addItems(self.app.regex_folders.values())
        self.wafer_flat_combo.setCurrentText(self.app.wafer_flat_data_path)
        # 경로가 변경될 때 호출될 메서드와 연결합니다.
        self.wafer_flat_combo.currentTextChanged.connect(self.update_wafer_flat_path)
        # "Clear" 버튼을 생성하고, 클릭 시 경로를 초기화하는 메서드와 연결합니다.
        self.wafer_flat_clear_button = QPushButton("Clear")
        self.wafer_flat_clear_button.clicked.connect(self.clear_wafer_flat_path)

        # 위젯들을 레이아웃에 추가합니다.
        wafer_flat_layout.addWidget(self.wafer_flat_label)
        wafer_flat_layout.addWidget(self.wafer_flat_combo)
        wafer_flat_layout.addWidget(self.wafer_flat_clear_button)

        # PreAlign Data Path 섹션
        # 프리얼라인 데이터 경로를 선택하는 섹션입니다.
        prealign_layout = QHBoxLayout()
        self.prealign_label = QLabel("PreAlign Data Path")
        self.prealign_combo = QComboBox()
        self.prealign_combo.addItem("Unselected")
        self.prealign_combo.addItems(self.app.regex_folders.values())
        self.prealign_combo.setCurrentText(self.app.prealign_data_path)
        self.prealign_combo.currentTextChanged.connect(self.update_prealign_path)
        self.prealign_clear_button = QPushButton("Clear")
        self.prealign_clear_button.clicked.connect(self.clear_prealign_path)

        prealign_layout.addWidget(self.prealign_label)
        prealign_layout.addWidget(self.prealign_combo)
        prealign_layout.addWidget(self.prealign_clear_button)

        # Image Data Path 섹션
        # 이미지 데이터 경로를 선택하는 섹션입니다.
        image_data_layout = QHBoxLayout()
        self.image_data_label = QLabel("Image Data Path")
        self.image_data_combo = QComboBox()
        self.image_data_combo.addItem("Unselected")
        self.image_data_combo.addItems(self.app.regex_folders.values())
        self.image_data_combo.setCurrentText(self.app.image_data_path)
        self.image_data_combo.currentTextChanged.connect(self.update_image_data_path)
        self.image_data_clear_button = QPushButton("Clear")
        self.image_data_clear_button.clicked.connect(self.clear_image_data_path)

        image_data_layout.addWidget(self.image_data_label)
        image_data_layout.addWidget(self.image_data_combo)
        image_data_layout.addWidget(self.image_data_clear_button)

        # 모든 UI 요소를 데이터베이스 레이아웃에 추가합니다.
        database_layout.addLayout(wafer_flat_layout)
        database_layout.addLayout(prealign_layout)
        database_layout.addLayout(image_data_layout)

        # 그룹박스 레이아웃을 설정합니다.
        database_group.setLayout(database_layout)

        # 그룹박스를 메인 레이아웃에 추가합니다.
        main_layout.addWidget(database_group)
        
        # 최종적으로 메인 레이아웃을 이 위젯의 레이아웃으로 설정합니다.
        self.setLayout(main_layout)

    def update_wafer_flat_path(self, text):
        # 웨이퍼 플랫 데이터 경로를 업데이트합니다.
        self.app.wafer_flat_data_path = text
        self.update_settings()

    def clear_wafer_flat_path(self):
        # 웨이퍼 플랫 데이터 경로를 초기화합니다.
        self.wafer_flat_combo.setCurrentText("Unselected")

    def update_prealign_path(self, text):
        # 프리얼라인 데이터 경로를 업데이트합니다.
        self.app.prealign_data_path = text
        self.update_settings()

    def clear_prealign_path(self):
        # 프리얼라인 데이터 경로를 초기화합니다.
        self.prealign_combo.setCurrentText("Unselected")

    def update_image_data_path(self, text):
        # 이미지 데이터 경로를 업데이트합니다.
        self.app.image_data_path = text
        self.update_settings()

    def clear_image_data_path(self):
        # 이미지 데이터 경로를 초기화합니다.
        self.image_data_combo.setCurrentText("Unselected")

    def update_settings(self):
        # 모든 설정을 저장합니다.
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
        """Upload Data 탭의 컨트롤들을 활성화 또는 비활성화합니다."""
        self.wafer_flat_combo.setEnabled(enabled)
        self.wafer_flat_clear_button.setEnabled(enabled)
        self.prealign_combo.setEnabled(enabled)
        self.prealign_clear_button.setEnabled(enabled)
        self.image_data_combo.setEnabled(enabled)
        self.image_data_clear_button.setEnabled(enabled)
