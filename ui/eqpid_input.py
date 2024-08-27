from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

# 이 모듈은 EQPID(장비 식별자)를 입력받기 위한 간단한 대화상자를 구현합니다.

class EqpidInputDialog(QDialog):
    def __init__(self, parent=None):
        # 부모 클래스(QDialog)의 초기화 메서드를 호출하여 대화상자를 설정합니다.
        super().__init__(parent)
        # 대화상자의 제목을 설정합니다.
        self.setWindowTitle("Enter EQPID")
        # UI 요소를 초기화합니다.
        self.initUI()

    def initUI(self):
        # 대화상자에 사용할 레이아웃을 설정합니다.
        layout = QVBoxLayout()

        # 라벨을 생성하여 사용자에게 EQPID를 입력하라는 메시지를 표시합니다.
        self.label = QLabel("Please enter the EQPID:")
        # EQPID를 입력받을 텍스트 입력란(QLineEdit)을 생성합니다.
        self.eqpid_input = QLineEdit()

        # 'OK' 버튼을 생성하여 사용자가 입력을 완료하고 대화상자를 닫을 수 있도록 합니다.
        self.ok_button = QPushButton("OK")
        # 'OK' 버튼이 클릭되면 accept() 메서드가 호출되어 대화상자가 닫힙니다.
        self.ok_button.clicked.connect(self.accept)

        # 라벨, 입력란, 버튼을 레이아웃에 추가합니다.
        layout.addWidget(self.label)
        layout.addWidget(self.eqpid_input)
        layout.addWidget(self.ok_button)

        # 대화상자에 설정한 레이아웃을 적용합니다.
        self.setLayout(layout)

    def get_eqpid(self):
        # 사용자가 입력한 EQPID를 반환하는 메서드입니다.
        return self.eqpid_input.text()
