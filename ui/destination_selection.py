from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox
from config import save_settings

class DestinationSelectionFrame(QWidget):
    def __init__(self, parent=None, app_context=None):
        # DestinationSelectionFrame 클래스는 폴더 선택과 관련된 UI 요소를 관리합니다.
        # parent: 부모 위젯 (None이면 최상위 위젯이 됩니다).
        # app_context: 애플리케이션의 현재 상태와 설정을 포함하는 객체입니다.
        super().__init__(parent)
        self.app_context = app_context
        # UI를 초기화합니다.
        self.initUI()

    def initUI(self):
        # UI 요소를 설정하는 메서드입니다.
        layout = QVBoxLayout()  # 세로로 위젯을 배치할 레이아웃을 만듭니다.

        # 'Save to Folder'라는 제목의 라벨을 만듭니다.
        self.label = QLabel("\u25cf Save to Folder")
        font = self.label.font()
        font.setBold(True)  # 라벨 텍스트를 굵게 설정합니다.
        self.label.setFont(font)

        # 현재 선택된 폴더를 표시하는 라벨을 만듭니다.
        # 선택된 폴더가 없다면 'No folder selected'라고 표시됩니다.
        self.pathLabel = QLabel(self.app_context.dest_folder if self.app_context.dest_folder else "No folder selected")  # type: ignore

        # 폴더 선택 버튼을 수평으로 배치하기 위한 레이아웃을 만듭니다.
        self.buttonLayout = QHBoxLayout()
        
        # 'Select Folder' 버튼을 만듭니다.
        self.selectButton = QPushButton("Select Folder")
        # 버튼이 클릭되었을 때 select_destination_folder 메서드를 호출하도록 설정합니다.
        self.selectButton.clicked.connect(self.select_destination_folder)
        
        # 버튼을 레이아웃에 추가합니다.
        self.buttonLayout.addWidget(self.selectButton)
        
        # 위에서 만든 라벨과 버튼을 레이아웃에 추가합니다.
        layout.addWidget(self.label)
        layout.addWidget(self.pathLabel)
        layout.addLayout(self.buttonLayout)
        
        # 최종적으로 이 위젯의 레이아웃을 설정합니다.
        self.setLayout(layout)

    def select_destination_folder(self):
        # 폴더 선택 버튼이 클릭되었을 때 호출되는 메서드입니다.
        # 애플리케이션의 설정 상태가 올바르게 설정되어 있는지 확인합니다.
        if self.app_context is None or not hasattr(self.app_context, 'dest_folder') or not hasattr(self.app_context, 'regex_folders'):
            QMessageBox.warning(self, "Error", "Application context is not properly set.")
            return

        # 폴더 선택 대화 상자를 엽니다.
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder", "", QFileDialog.Option.ShowDirsOnly)
        
        # 사용자가 폴더를 선택한 경우
        if folder:
            # 선택된 폴더 경로를 애플리케이션 설정에 저장합니다.
            self.app_context.dest_folder = folder
            # 경로 라벨에 선택된 폴더 경로를 표시합니다.
            self.pathLabel.setText(folder)
            # 설정을 저장합니다.
            save_settings(self.app_context.monitored_folders, self.app_context.dest_folder, self.app_context.regex_folders, self.app_context.exclude_folders, self.app_context.base_date_folder, self.app_context.target_compare_folders)	# type: ignore
