from PySide6.QtWidgets import QWidget, QPushButton, QListView, QLabel, QVBoxLayout, QHBoxLayout, QInputDialog, QMessageBox, QFileDialog
from PySide6.QtCore import QStringListModel
from config import save_settings

class RegexManagementFrame(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app  # 앱의 전역 설정 및 상태를 관리하는 객체
        self.initUI()  # UI 요소들을 초기화하는 메서드 호출

    def initUI(self):
        # 전체 레이아웃을 세로로 배치
        layout = QVBoxLayout()

        # "Regex Categorization" 레이블을 추가
        self.regex_label = QLabel("\u25cf Regex Categorization")
        font = self.regex_label.font()
        font.setBold(True)  # 레이블을 굵게 설정
        self.regex_label.setFont(font)
        
        # 리스트 뷰를 만들어, 정규 표현식 패턴들을 보여줄 공간을 준비
        self.regex_list = QListView()
        
        # 정규 표현식을 추가, 편집, 삭제할 버튼들을 생성
        self.regex_add_button = QPushButton("Add Regex")
        self.regex_edit_button = QPushButton("Edit Regex")
        self.regex_remove_button = QPushButton("Remove")
        
        # 버튼들을 세로로 배치
        self.regex_button_layout = QVBoxLayout()
        self.regex_button_layout.addWidget(self.regex_add_button)
        self.regex_button_layout.addWidget(self.regex_edit_button)
        self.regex_button_layout.addWidget(self.regex_remove_button)

        # 버튼 클릭 시 호출될 메서드들을 연결
        self.regex_add_button.clicked.connect(self.add_regex)
        self.regex_edit_button.clicked.connect(self.edit_regex)
        self.regex_remove_button.clicked.connect(self.remove_regex)

        # 정규 표현식 리스트와 버튼 레이아웃을 수평으로 배치
        regex_layout = QHBoxLayout()
        regex_layout.addWidget(self.regex_list)
        regex_layout.addLayout(self.regex_button_layout)

        # 레이아웃을 최종적으로 설정
        layout.addWidget(self.regex_label)
        layout.addLayout(regex_layout)
        self.setLayout(layout)
        
        # UI가 초기화된 후 리스트를 업데이트
        self.update_regex_list()

    def add_regex(self):
        # 사용자에게 정규 표현식 패턴을 입력받음
        pattern, ok = QInputDialog.getText(self, "Input", "Enter regex pattern:")
        if ok and pattern:  # 입력이 확인되었을 경우
            subfolder = self.select_subfolder()  # 해당 정규 표현식에 매칭될 폴더 선택
            if subfolder:
                # 정규 표현식과 선택된 폴더를 앱의 설정에 추가
                self.app.regex_folders[pattern] = subfolder
                save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)
                self.update_regex_list()  # 리스트를 업데이트

    def edit_regex(self):
        # 리스트에서 선택된 정규 표현식을 편집
        selected = self.regex_list.selectedIndexes()
        if not selected:  # 선택된 항목이 없을 경우 경고 메시지 표시
            QMessageBox.warning(self, "Warning", "No pattern selected.")
            return
        selected_index = selected[0].row()  # 선택된 항목의 인덱스 가져오기
        pattern = list(self.app.regex_folders.keys())[selected_index]
        subfolder = self.app.regex_folders[pattern]
        # 기존의 패턴을 보여주고 수정할 수 있도록 대화상자를 표시
        new_pattern, ok = QInputDialog.getText(self, "Input", "Edit regex pattern:", text=pattern)
        if ok and new_pattern:
            # 새로운 폴더 선택
            new_subfolder = self.select_subfolder(default_path=subfolder)
            if new_subfolder:
                # 기존 패턴 삭제 후 새로운 패턴과 폴더를 저장
                del self.app.regex_folders[pattern]
                self.app.regex_folders[new_pattern] = new_subfolder
                save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)
                self.update_regex_list()  # 리스트를 업데이트

    def remove_regex(self):
        # 선택된 정규 표현식을 삭제
        selected = self.regex_list.selectedIndexes()
        for index in sorted([idx.row() for idx in selected], reverse=True):
            pattern = list(self.app.regex_folders.keys())[index]
            del self.app.regex_folders[pattern]
        # 삭제된 후 설정을 저장하고 리스트를 업데이트
        save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)
        self.update_regex_list()

    def update_regex_list(self):
        # 현재 앱의 설정에서 정규 표현식 목록을 가져와 리스트 뷰를 업데이트
        model = QStringListModel([f"{pattern} -> {subfolder}" for pattern, subfolder in self.app.regex_folders.items()])
        self.regex_list.setModel(model)

    def select_subfolder(self, default_path=''):
        # 사용자가 선택한 폴더 경로를 반환
        folder = QFileDialog.getExistingDirectory(self, "Select Subfolder", default_path, QFileDialog.Option.ShowDirsOnly)
        return folder if folder else None

    def set_controls_enabled(self, enabled):
        """정규 표현식 관리에 대한 UI 요소를 활성화 또는 비활성화"""
        self.regex_list.setEnabled(enabled)
        self.regex_add_button.setEnabled(enabled)
        self.regex_edit_button.setEnabled(enabled)
        self.regex_remove_button.setEnabled(enabled)
