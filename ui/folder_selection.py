from PySide6.QtWidgets import QWidget, QPushButton, QListView, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QLabel
from PySide6.QtCore import QStringListModel
from config import save_settings

# FolderSelectionFrame 클래스는 사용자가 모니터링할 폴더를 선택하고 관리할 수 있는 UI 프레임입니다.
class FolderSelectionFrame(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app  # 애플리케이션의 전체 설정을 담고 있는 컨텍스트 객체
        self.initUI()  # UI를 초기화하는 메서드를 호출

    def initUI(self):
        # UI를 구성하는 메서드
        layout = QVBoxLayout()

        # 폴더 선택 섹션의 제목을 나타내는 라벨을 생성
        self.label = QLabel("\u25cf Folders to Monitor")  # "모니터링할 폴더"라는 제목
        font = self.label.font()
        font.setBold(True)  # 제목을 굵게 설정
        self.label.setFont(font)

        # 폴더 목록을 보여주는 리스트뷰를 생성
        self.listView = QListView()
        self.listView.setFixedHeight(150)  # 리스트뷰의 높이를 150으로 설정

        # 폴더 선택과 제거 버튼을 배치할 레이아웃
        self.buttonLayout = QHBoxLayout()

        # 폴더 선택 버튼을 생성하고 클릭 이벤트에 select_folders 메서드를 연결
        self.selectButton = QPushButton("Select Folders")
        self.selectButton.clicked.connect(self.select_folders)

        # 폴더 제거 버튼을 생성하고 클릭 이벤트에 remove_selected_folders 메서드를 연결
        self.removeButton = QPushButton("Remove")
        self.removeButton.clicked.connect(self.remove_selected_folders)

        # 버튼을 레이아웃에 추가
        self.buttonLayout.addWidget(self.selectButton)
        self.buttonLayout.addWidget(self.removeButton)

        # 전체 레이아웃에 각 요소들을 추가
        layout.addWidget(self.label)
        layout.addWidget(self.listView)
        layout.addLayout(self.buttonLayout)

        # 레이아웃을 위젯에 설정
        self.setLayout(layout)

        # 현재 선택된 폴더 목록을 업데이트
        self.update_listView()

    # 사용자가 새로운 폴더를 선택할 때 호출되는 메서드
    def select_folders(self):
        if self.app is None or not hasattr(self.app, 'monitored_folders'):
            # 애플리케이션 컨텍스트가 올바르게 설정되지 않았을 때 경고 메시지 표시
            QMessageBox.warning(self, "Error", "Application context is not properly set.")
            return
        
        # 사용자가 폴더를 선택할 수 있는 파일 다이얼로그를 엽니다.
        folder = QFileDialog.getExistingDirectory(self, "Select Folders to Monitor", "", QFileDialog.Option.ShowDirsOnly)
        if folder:
            # 선택된 폴더를 애플리케이션의 모니터링 폴더 목록에 추가
            self.app.monitored_folders.append(folder)
            # 설정을 저장
            save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)   # type: ignore
            # 리스트뷰를 업데이트
            self.update_listView()

    # 사용자가 선택된 폴더를 제거할 때 호출되는 메서드
    def remove_selected_folders(self):
        if self.app is None or not hasattr(self.app, 'monitored_folders'):
            # 애플리케이션 컨텍스트가 올바르게 설정되지 않았을 때 경고 메시지 표시
            QMessageBox.warning(self, "Error", "Application context is not properly set.")
            return
        
        # 선택된 항목의 인덱스를 가져옴
        selected = self.listView.selectedIndexes()
        # 선택된 폴더들을 목록에서 삭제
        for index in sorted([index.row() for index in selected], reverse=True):
            del self.app.monitored_folders[index]
        # 변경된 설정을 저장
        save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)   # type: ignore
        # 리스트뷰를 업데이트
        self.update_listView()

    # 폴더 목록을 업데이트하는 메서드
    def update_listView(self):
        if self.app is None or not hasattr(self.app, 'monitored_folders'):
            # 애플리케이션 컨텍스트가 올바르게 설정되지 않았을 때 경고 메시지 표시
            QMessageBox.warning(self, "Error", "Application context is not properly set.")
            return
        
        # 현재 모니터링하는 폴더 목록을 리스트뷰에 표시할 수 있도록 모델로 설정
        model = QStringListModel(self.app.monitored_folders)
        self.listView.setModel(model)
