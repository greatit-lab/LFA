from PySide6.QtWidgets import QWidget, QPushButton, QListView, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QLabel
from PySide6.QtCore import QStringListModel
from config import save_settings

# ExcludeFolderSelectionFrame 클래스는 사용자가 모니터링에서 제외할 폴더를 선택하고 관리할 수 있는 UI를 제공합니다.
class ExcludeFolderSelectionFrame(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app  # 애플리케이션 컨텍스트를 설정합니다.
        self.initUI()  # UI를 초기화합니다.

    # UI 초기화를 위한 메서드입니다.
    def initUI(self):
        layout = QVBoxLayout()  # 전체 레이아웃을 수직으로 구성합니다.

        # "Folders to Exclude from Monitoring"이라는 라벨을 생성하고 굵은 글씨로 설정합니다.
        self.label = QLabel("\u25cf Folders to Exclude from Monitoring")
        font = self.label.font()
        font.setBold(True)
        self.label.setFont(font)

        # 폴더 목록을 보여줄 QListView를 생성합니다.
        self.listView = QListView()
        self.listView.setFixedHeight(150)  # 목록의 높이를 150 픽셀로 고정합니다.

        # 폴더 선택과 제거 버튼을 가로로 배치하기 위한 레이아웃을 생성합니다.
        self.buttonLayout = QHBoxLayout()
        self.selectButton = QPushButton("Select Folders")  # 폴더 선택 버튼을 생성합니다.
        self.removeButton = QPushButton("Remove")  # 폴더 제거 버튼을 생성합니다.
        self.selectButton.clicked.connect(self.select_folders)  # 폴더 선택 버튼 클릭 시 호출할 메서드를 연결합니다.
        self.removeButton.clicked.connect(self.remove_selected_folders)  # 폴더 제거 버튼 클릭 시 호출할 메서드를 연결합니다.
        self.buttonLayout.addWidget(self.selectButton)
        self.buttonLayout.addWidget(self.removeButton)

        # 레이아웃을 구성하고, 현재 UI의 레이아웃으로 설정합니다.
        layout.addWidget(self.label)
        layout.addWidget(self.listView)
        layout.addLayout(self.buttonLayout)
        self.setLayout(layout)

        # 폴더 목록을 업데이트합니다.
        self.update_listView()

    # 폴더 선택 버튼이 클릭되었을 때 호출되는 메서드입니다.
    def select_folders(self):
        # 애플리케이션 컨텍스트가 올바르게 설정되었는지 확인합니다.
        if self.app is None or not hasattr(self.app, 'exclude_folders'):
            QMessageBox.warning(self, "Error", "Application context is not properly set.")
            return

        # 폴더 선택 대화상자를 열어 사용자가 폴더를 선택하도록 합니다.
        folder = QFileDialog.getExistingDirectory(self, "Select Folders to Exclude from Monitoring", "", QFileDialog.Option.ShowDirsOnly)
        if folder:
            # 선택된 폴더를 제외 목록에 추가하고 설정을 저장합니다.
            self.app.exclude_folders.append(folder)
            save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)   # type: ignore
            self.update_listView()  # 폴더 목록을 업데이트합니다.

    # 폴더 제거 버튼이 클릭되었을 때 호출되는 메서드입니다.
    def remove_selected_folders(self):
        # 애플리케이션 컨텍스트가 올바르게 설정되었는지 확인합니다.
        if self.app is None or not hasattr(self.app, 'exclude_folders'):
            QMessageBox.warning(self, "Error", "Application context is not properly set.")
            return

        # 선택된 폴더들을 제외 목록에서 제거하고 설정을 저장합니다.
        selected = self.listView.selectedIndexes()
        for index in sorted([index.row() for index in selected], reverse=True):
            del self.app.exclude_folders[index]
        save_settings(self.app.monitored_folders, self.app.dest_folder, self.app.regex_folders, self.app.exclude_folders, self.app.base_date_folder, self.app.target_compare_folders)   # type: ignore
        self.update_listView()  # 폴더 목록을 업데이트합니다.

    # QListView에 폴더 목록을 업데이트하는 메서드입니다.
    def update_listView(self):
        # 애플리케이션 컨텍스트가 올바르게 설정되었는지 확인합니다.
        if self.app is None or not hasattr(self.app, 'exclude_folders'):
            QMessageBox.warning(self, "Error", "Application context is not properly set.")
            return

        # 제외할 폴더들의 목록을 QStringListModel로 설정하여 QListView에 표시합니다.
        model = QStringListModel(self.app.exclude_folders)
        self.listView.setModel(model)
