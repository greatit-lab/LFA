from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QListView, QFileDialog, QMessageBox
from PySide6.QtCore import QStringListModel
from config import save_settings
import os

class OverrideNamesFrame(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app  # 앱 컨텍스트를 초기화합니다.
        self.initUI()  # UI를 초기화하는 메서드를 호출합니다.

    def initUI(self):
        # 전체 레이아웃을 설정합니다.
        layout = QVBoxLayout()

        # Base Date File Path 섹션을 설정합니다.
        self.base_date_label = QLabel("\u25cf Base Date File Path (Date)")
        font = self.base_date_label.font()
        font.setBold(True)  # 레이블을 굵게 설정합니다.
        self.base_date_label.setFont(font)
        self.base_date_combo = QComboBox()  # 콤보박스를 생성합니다.
        self.base_date_combo.addItem("Unselected")  # 기본 선택 항목을 추가합니다.
        self.base_date_clear_button = QPushButton("Clear")  # Clear 버튼을 생성합니다.
        base_date_layout = QHBoxLayout()  # Base Date 레이아웃을 설정합니다.
        base_date_layout.addWidget(self.base_date_combo)
        base_date_layout.addWidget(self.base_date_clear_button)

        # 콤보박스의 선택 항목이 변경되었을 때 호출될 메서드를 연결합니다.
        self.base_date_combo.currentTextChanged.connect(self.update_base_date_path)
        # Clear 버튼이 클릭되었을 때 호출될 메서드를 연결합니다.
        self.base_date_clear_button.clicked.connect(self.clear_base_date)

        # Target Compare File Paths 섹션을 설정합니다.
        self.target_compare_label = QLabel("\u25cf Target compare file paths (Slot)")
        font = self.target_compare_label.font()
        font.setBold(True)  # 레이블을 굵게 설정합니다.
        self.target_compare_label.setFont(font)
        self.target_compare_list = QListView()  # 리스트 뷰를 생성합니다.
        self.target_compare_add_button = QPushButton("Select Folders")  # 폴더 선택 버튼을 생성합니다.
        self.target_compare_remove_button = QPushButton("Remove")  # 폴더 제거 버튼을 생성합니다.
        target_compare_button_layout = QVBoxLayout()  # 버튼 레이아웃을 설정합니다.
        target_compare_button_layout.addWidget(self.target_compare_add_button)
        target_compare_button_layout.addWidget(self.target_compare_remove_button)

        # 폴더 선택 버튼과 폴더 제거 버튼의 클릭 이벤트를 연결합니다.
        self.target_compare_add_button.clicked.connect(self.add_target_compare_path)
        self.target_compare_remove_button.clicked.connect(self.remove_target_compare_path)

        # Target Compare 섹션의 레이아웃을 설정합니다.
        target_compare_layout = QHBoxLayout()
        target_compare_layout.addWidget(self.target_compare_list)
        target_compare_layout.addLayout(target_compare_button_layout)

        # 전체 레이아웃에 섹션들을 추가합니다.
        layout.addWidget(self.base_date_label)
        layout.addLayout(base_date_layout)
        layout.addWidget(self.target_compare_label)
        layout.addLayout(target_compare_layout)
        self.setLayout(layout)

        # 콤보박스와 리스트 뷰를 초기화합니다.
        self.update_base_date_combo()
        self.update_target_compare_list()

    def update_base_date_combo(self):
        """기본 날짜 콤보박스를 업데이트합니다."""
        current_selection = self.base_date_combo.currentText()
        
        self.base_date_combo.blockSignals(True)  # 신호를 일시적으로 차단하여 불필요한 신호를 방지
        
        self.base_date_combo.clear()
        self.base_date_combo.addItem("Unselected")  # 기본값을 추가합니다.
        self.base_date_combo.addItems(self.app.regex_folders.values())      # type: ignore  # 앱의 폴더 값을 추가합니다.
        
        # 기존의 선택이 유지될 수 있도록 설정
        if current_selection in self.app.regex_folders.values():    # type: ignore
            self.base_date_combo.setCurrentText(current_selection)
        else:
            # 만약 current_selection이 초기화된 리스트에 없다면, 설정 파일에서 불러온 값을 사용
            self.base_date_combo.setCurrentText(self.app.base_date_folder)      # type: ignore
        
        self.base_date_combo.blockSignals(False)  # 신호를 다시 활성화

    def clear_base_date(self):
        """기본 날짜 콤보박스를 'Unselected'로 초기화합니다."""
        self.base_date_combo.setCurrentIndex(0)

    def update_base_date_path(self, text):
        """기본 날짜 경로를 업데이트하고 설정을 저장합니다."""
        self.app.base_date_folder = text    # type: ignore
        self.update_settings()

    def add_target_compare_path(self):
        """대상 비교 경로를 추가합니다."""
        save_to_folder = self.app.dest_folder   # type: ignore
        folder = QFileDialog.getExistingDirectory(self, "Select Target Compare Folder", save_to_folder, QFileDialog.Option.ShowDirsOnly)
        if folder:
            normalized_folder = os.path.normpath(folder)  # 선택된 폴더 경로를 정규화합니다.
            if not normalized_folder.startswith(os.path.abspath(save_to_folder)):
                QMessageBox.warning(self, "Warning", f"Please select a folder within {save_to_folder}.")
                return
            self.app.target_compare_folders.append(normalized_folder)   # type: ignore
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
                self.app.image_data_path,
                self.app.error_data_path,
                self.app.event_data_path,
                self.app.wave_data_path
            )   # type: ignore
            if self.app.logger:     # type: ignore
                self.app.logger.log_event("Target Compare Folder Added", folder)    # type: ignore
                self.app.logger.log_debug(f"Target compare folder added: {folder}")     # type: ignore
            self.update_target_compare_list()

    def remove_target_compare_path(self):
        """선택된 대상 비교 경로를 제거합니다."""
        selected = self.target_compare_list.selectedIndexes()
        for index in sorted(selected, key=lambda idx: idx.row(), reverse=True):
            folder = self.app.target_compare_folders[index.row()]   # type: ignore
            del self.app.target_compare_folders[index.row()]    # type: ignore
            if self.app.logger:     # type: ignore
                self.app.logger.log_event("Target Compare Folder Removed", folder)      # type: ignore
                self.app.logger.log_debug(f"Target compare folder removed: {folder}")   # type: ignore
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
            self.app.image_data_path,
            self.app.error_data_path,
            self.app.event_data_path,
            self.app.wave_data_path
        )
        self.update_target_compare_list()

    def update_target_compare_list(self):
        """대상 비교 경로 리스트를 업데이트합니다."""
        normalized_folders = [os.path.normpath(folder) for folder in self.app.target_compare_folders]   # type: ignore  # 폴더 경로를 정규화합니다.
        model = QStringListModel(normalized_folders)
        self.target_compare_list.setModel(model)

    def set_controls_enabled(self, enabled):
        """override names 탭의 모든 컨트롤을 활성화 또는 비활성화합니다."""
        self.base_date_combo.setEnabled(enabled)
        self.base_date_clear_button.setEnabled(enabled)
        self.target_compare_list.setEnabled(enabled)
        self.target_compare_add_button.setEnabled(enabled)
        self.target_compare_remove_button.setEnabled(enabled)

    def update_settings(self):
        """설정을 저장합니다."""
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
            self.app.image_data_path,
            self.app.error_data_path,
            self.app.event_data_path,
            self.app.wave_data_path
        )   # type: ignore
