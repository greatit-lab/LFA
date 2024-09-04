import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMenu, QSystemTrayIcon, QTabWidget, QLabel
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from ui.folder_monitor import FolderMonitorFrame
from ui.regex_management import RegexManagementFrame
from ui.monitoring_controls import MonitoringControls
from ui.override_names import OverrideNamesFrame
from ui.image_trans import ImageTransFrame
from ui.upload_data import UploadDataFrame  # 데이터 업로드 탭을 위한 프레임 추가
from tray_icon import run_tray_icon
from threading import Thread, Event
from event_handler import EventLogger
from config import load_settings, save_settings

# 리소스 파일의 절대 경로를 반환하는 함수입니다.
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# 애플리케이션의 설정 및 데이터를 관리하는 컨텍스트 클래스입니다.
class AppContext:
    def __init__(self):
        # 설정 파일에서 데이터를 불러옵니다.
        (
            self.monitored_folders, self.dest_folder, self.regex_folders, self.exclude_folders, self.base_date_folder,
            self.target_compare_folders, self.target_image_folder, self.wait_time, self.image_save_folder, self.wafer_flat_data_path,
            self.prealign_data_path, self.image_data_path, self.error_data_path, self.event_data_path, self.wave_data_path
        ) = load_settings()

    # 현재 설정을 저장하는 함수입니다.
    def save_settings(self):
        save_settings(
            self.monitored_folders,
            self.dest_folder,
            self.regex_folders,
            self.exclude_folders,
            self.base_date_folder,
            self.target_compare_folders,
            self.target_image_folder,
            self.wait_time,
            self.image_save_folder,
            self.wafer_flat_data_path,
            self.prealign_data_path,
            self.image_data_path,
            self.error_data_path,
            self.event_data_path,
            self.wave_data_path
        )

# 메인 애플리케이션 클래스입니다. QMainWindow를 상속하여 GUI의 메인 창을 관리합니다.
class MonitorApp(QMainWindow):
    def __init__(self, app_context, base_dir):
        super().__init__()
        self.app_context = app_context  # 앱 컨텍스트를 저장합니다.
        self.base_dir = base_dir  # 베이스 디렉토리를 저장합니다.
        self.stop_event = Event()  # 모니터링 중지를 위한 이벤트 객체를 생성합니다.
        self.logger = EventLogger(self.base_dir)  # 로그 기록을 위한 Logger 객체를 생성합니다.
        self.initUI()  # UI를 초기화합니다.

    # 메인 UI를 초기화하고 탭과 트레이 아이콘을 설정합니다.
    def initUI(self):
        self.setWindowTitle("LogFusion Agent - alpha")
        icon_path = resource_path("resources/icons/icon.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)  # type: ignore  # 최대화 버튼을 비활성화합니다.
        self.resize(600, 400)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # EQPID 정보를 표시하는 라벨을 추가합니다.
        eqpid_label = QLabel(f"EQPID : {self.app_context.eqpid}")
        layout.addWidget(eqpid_label)

        self.tabs = QTabWidget()  # 탭 위젯을 생성합니다.
        # 각 탭을 생성하고 추가합니다.
        self.folder_monitor_frame = FolderMonitorFrame(app=self.app_context)
        self.regex_management_frame = RegexManagementFrame(app=self.app_context)
        self.override_names_frame = OverrideNamesFrame(app=self.app_context)
        self.image_trans_frame = ImageTransFrame(app=self.app_context)  # 이미지 변환 탭 추가
        self.upload_data_frame = UploadDataFrame(app=self.app_context)  # 데이터 업로드 탭 추가
        self.monitoring_controls = MonitoringControls(parent=self, app=self)

        # 생성한 탭을 UI에 추가합니다.
        self.tabs.addTab(self.folder_monitor_frame, "Monitor Settings")
        self.tabs.addTab(self.regex_management_frame, "Regex")
        self.tabs.addTab(self.override_names_frame, "Override Names")
        self.tabs.addTab(self.image_trans_frame, "Image Trans")  # 이미지 변환 탭 추가
        self.tabs.addTab(self.upload_data_frame, "Upload Data")  # 데이터 업로드 탭 추가

        layout.addWidget(self.tabs)
        layout.addWidget(self.monitoring_controls)

        # Override Names 탭의 base_date_combo의 초기 값을 설정합니다.
        self.override_names_frame.base_date_combo.setCurrentText(self.app_context.base_date_folder)

        # 시스템 트레이 아이콘을 설정합니다.
        self.tray_icon = run_tray_icon(self)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    # 모니터링을 시작하는 함수입니다.
    def start_monitoring(self):
        self.monitoring_controls.start_monitoring()

    # 모니터링을 중지하는 함수입니다.
    def stop_monitoring(self):
        self.monitoring_controls.stop_monitoring()

    # 애플리케이션을 종료하는 함수입니다.
    def quit_app(self):
        self.monitoring_controls.quit_app()

    # 창을 닫을 때 호출되는 이벤트 핸들러입니다.
    def closeEvent(self, event):
        self.hide()
        event.ignore()  # 창을 닫지 않고 숨깁니다.

    # 트레이 아이콘을 더블 클릭했을 때 창을 보여주는 함수입니다.
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:   # type: ignore
            self.show_window()

    # 트레이 아이콘의 메뉴를 업데이트하는 함수입니다.
    def update_tray_menu(self):
        self.tray_icon.contextMenu().clear()
        menu = QMenu()
        show_action = menu.addAction("Show")
        show_action.triggered.connect(self.show_window)
        run_action = menu.addAction("Run")
        run_action.setEnabled(self.monitoring_controls.status_label.text() in ["Status: Idle", "Status: Stopped"])
        run_action.triggered.connect(self.start_monitoring)
        stop_action = menu.addAction("Stop")
        stop_action.setEnabled(self.monitoring_controls.status_label.text() == "Status: Monitoring")
        stop_action.triggered.connect(self.stop_monitoring)
        quit_action = menu.addAction("Quit")
        quit_action.setEnabled(self.monitoring_controls.status_label.text() in ["Status: Stopped", "Status: Idle"])
        quit_action.triggered.connect(self.quit_app)
        self.tray_icon.setContextMenu(menu)

    # 메인 창을 화면에 표시하는 함수입니다.
    def show_window(self):
        self.show()
        self.activateWindow()  # 창을 활성화합니다.
