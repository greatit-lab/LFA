from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListView, QPushButton, QHBoxLayout, QComboBox, QInputDialog, QMessageBox, QFileDialog
from PySide6.QtCore import QStringListModel
from config import save_settings

class SeparationFrame(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        self.initUI()

    def initUI(self):
        # UI 초기화 메서드로, 인터페이스의 레이아웃과 구성 요소들을 설정합니다.
        layout = QVBoxLayout()

        # Regex Categorization 섹션의 UI 설정
        self.regex_label = QLabel("\u25cf Regex Categorization")  # Regex 분류 섹션의 제목을 설정
        font = self.regex_label.font()
        font.setBold(True)  # 제목의 폰트를 굵게 설정
        self.regex_label.setFont(font)
        self.regex_list = QListView()  # Regex 리스트를 표시할 QListView 생성
        self.regex_add_button = QPushButton("Add Regex")  # Regex 추가 버튼
        self.regex_edit_button = QPushButton("Edit Regex")  # Regex 편집 버튼
        self.regex_remove_button = QPushButton("Remove")  # Regex 제거 버튼
        self.regex_button_layout = QVBoxLayout()  # 버튼들을 수직으로 배치하기 위한 레이아웃
        self.regex_button_layout.addWidget(self.regex_add_button)
        self.regex_button_layout.addWidget(self.regex_edit_button)
        self.regex_button_layout.addWidget(self.regex_remove_button)

        # 버튼들에 각 기능 연결
        self.regex_add_button.clicked.connect(self.add_regex)
        self.regex_edit_button.clicked.connect(self.edit_regex)
        self.regex_remove_button.clicked.connect(self.remove_regex)

        # Regex 섹션의 레이아웃 설정
        regex_layout = QHBoxLayout()
        regex_layout.addWidget(self.regex_list)
        regex_layout.addLayout(self.regex_button_layout)

        # Rename a Date 섹션의 UI 설정
        self.rename_label = QLabel("\u25cf Rename a Date")  # 날짜 변경 섹션의 제목을 설정
        font = self.rename_label.font()
        font.setBold(True)
        self.rename_label.setFont(font)
        self.rename_combo = QComboBox()  # 날짜 변경을 위한 콤보박스 생성
        self.rename_combo.addItem("Unselected")  # 기본 선택 옵션 설정
        self.rename_clear_button = QPushButton("Clear")  # 선택 해제 버튼 생성
        rename_layout = QHBoxLayout()  # 날짜 변경 섹션의 레이아웃 설정
        rename_layout.addWidget(self.rename_combo)
        rename_layout.addWidget(self.rename_clear_button)

        # Clear 버튼에 기능 연결
        self.rename_clear_button.clicked.connect(self.clear_rename)

        # 전체 레이아웃에 섹션들을 추가
        layout.addWidget(self.regex_label)
        layout.addLayout(regex_layout)
        layout.addWidget(self.rename_label)
        layout.addLayout(rename_layout)
        self.setLayout(layout)
        self.update_regex_list()  # 초기화 시 리스트 업데이트

    def add_regex(self):
        # 새로운 Regex 패턴을 추가하는 메서드
        pattern, ok = QInputDialog.getText(self, "Input", "Enter regex pattern:")
        if ok and pattern:
            subfolder = self.select_subfolder()
            if subfolder:
                self.app.regex_folders[pattern] = subfolder  # 새로운 패턴과 서브폴더를 앱 설정에 추가
                save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)
                self.update_regex_list()

    def edit_regex(self):
        # 기존의 Regex 패턴을 수정하는 메서드
        selected = self.regex_list.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, "Warning", "No pattern selected.")  # 패턴이 선택되지 않은 경우 경고 메시지 표시
            return
        selected_index = selected[0].row()
        pattern = list(self.app.regex_folders.keys())[selected_index]
        subfolder = self.app.regex_folders[pattern]
        new_pattern, ok = QInputDialog.getText(self, "Input", "Edit regex pattern:", text=pattern)
        if ok and new_pattern:
            new_subfolder = self.select_subfolder(default_path=subfolder)
            if new_subfolder:
                del self.app.regex_folders[pattern]
                self.app.regex_folders[new_pattern] = new_subfolder  # 새로운 패턴과 서브폴더를 설정에 업데이트
                save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)
                self.update_regex_list()

    def remove_regex(self):
        # 선택된 Regex 패턴을 제거하는 메서드
        selected = self.regex_list.selectedIndexes()
        for index in sorted([index.row() for index in selected], reverse=True):
            pattern = list(self.app.regex_folders.keys())[index]
            del self.app.regex_folders[pattern]  # 선택된 패턴을 설정에서 삭제
        save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)
        self.update_regex_list()

    def update_regex_list(self):
        # Regex 리스트와 콤보박스를 업데이트하는 메서드
        model = QStringListModel([f"{pattern} -> {subfolder}" for pattern, subfolder in self.app.regex_folders.items()])
        self.regex_list.setModel(model)
        self.rename_combo.clear()
        self.rename_combo.addItem("Unselected")  # 기본값 설정
        self.rename_combo.addItems(self.app.regex_folders.values())

    def clear_rename(self):
        # 날짜 변경 콤보박스를 초기화하는 메서드
        self.rename_combo.setCurrentIndex(0)  # 콤보박스를 "Unselected"로 되돌림

    def select_subfolder(self, default_path=''):
        # 서브폴더를 선택하는 파일 다이얼로그를 표시하는 메서드
        folder = QFileDialog.getExistingDirectory(self, "Select Subfolder", default_path, QFileDialog.Option.ShowDirsOnly)
        return folder if folder else None  # 선택된 폴더 경로를 반환, 선택되지 않으면 None 반환
