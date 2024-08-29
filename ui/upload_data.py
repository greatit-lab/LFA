from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QGroupBox
from configparser import ConfigParser
from config import save_settings
from upload.wafer_flat_data import WaferFlatHandler
from upload.prealign_data import PreAlignHandler
from upload.image_data import ImageDataHandler

class UploadDataFrame(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        self.eqpid = self.load_eqpid()  # EqpId 값을 로드합니다.
        self.initUI()

    def load_eqpid(self):
        config = ConfigParser()
        config.read('eqpid.ini')  # eqpid.ini 파일을 읽습니다.
        return config['DEFAULT'].get('EqpId', 'Unknown')  # EqpId 값을 가져옵니다.

    def initUI(self):
        main_layout = QVBoxLayout()

        # Database Uploading GroupBox
        database_group = QGroupBox("Database Uploading")
        database_layout = QVBoxLayout()

        # Wafer Flat Data Path
        wafer_flat_layout = QHBoxLayout()
        self.wafer_flat_label = QLabel("Wafer Flat Data Path")
        self.wafer_flat_combo = QComboBox()
        self.wafer_flat_combo.addItem("Unselected")
        self.wafer_flat_combo.addItems(self.app.regex_folders.values())
        self.wafer_flat_combo.setCurrentText(self.app.wafer_flat_data_path)
        self.wafer_flat_combo.currentTextChanged.connect(self.update_wafer_flat_path)
        self.wafer_flat_clear_button = QPushButton("Clear")
        self.wafer_flat_clear_button.clicked.connect(self.clear_wafer_flat_path)
        wafer_flat_layout.addWidget(self.wafer_flat_label)
        wafer_flat_layout.addWidget(self.wafer_flat_combo)
        wafer_flat_layout.addWidget(self.wafer_flat_clear_button)

        # PreAlign Data Path
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

        # Image Data Path
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

        # Add layouts to the database group layout
        database_layout.addLayout(wafer_flat_layout)
        database_layout.addLayout(prealign_layout)
        database_layout.addLayout(image_data_layout)

        database_group.setLayout(database_layout)
        main_layout.addWidget(database_group)

        self.setLayout(main_layout)

    def update_wafer_flat_path(self, text):
        self.app.wafer_flat_data_path = text
        self.update_settings()

    def clear_wafer_flat_path(self):
        self.wafer_flat_combo.setCurrentText("Unselected")

    def update_prealign_path(self, text):
        self.app.prealign_data_path = text
        self.update_settings()

    def clear_prealign_path(self):
        self.prealign_combo.setCurrentText("Unselected")

    def update_image_data_path(self, text):
        self.app.image_data_path = text
        self.update_settings()

    def clear_image_data_path(self):
        self.image_data_combo.setCurrentText("Unselected")

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
        self.wafer_flat_combo.setEnabled(enabled)
        self.wafer_flat_clear_button.setEnabled(enabled)
        self.prealign_combo.setEnabled(enabled)
        self.prealign_clear_button.setEnabled(enabled)
        self.image_data_combo.setEnabled(enabled)
        self.image_data_clear_button.setEnabled(enabled)
