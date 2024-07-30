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
from ui.upload_data import UploadDataFrame  # 이 줄을 추가하여 UploadDataFrame을 가져옵니다
from tray_icon import run_tray_icon
from threading import Thread, Event
from event_handler import EventLogger
from config import load_settings, save_settings

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class AppContext:
    def __init__(self):
        (self.monitored_folders, self.dest_folder, self.regex_folders, self.exclude_folders, 
         self.base_date_folder, self.target_compare_folders, self.target_image_folder, 
         self.wait_time, self.image_save_folder, self.wafer_flat_data_path, 
         self.prealign_data_path, self.image_data_path) = load_settings()

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
            self.image_data_path
        )
class MonitorApp(QMainWindow):
    def __init__(self, app_context, base_dir):
        super().__init__()
        self.app_context = app_context
        self.base_dir = base_dir
        self.stop_event = Event()
        self.logger = EventLogger(self.base_dir)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("LogFusion Agent - alpha")
        icon_path = resource_path("resources/icons/icon.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)  # Disable maximize button
        self.resize(600, 400)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add EQPID Label
        eqpid_label = QLabel(f"EQPID : {self.app_context.eqpid}")
        layout.addWidget(eqpid_label)

        self.tabs = QTabWidget()
        self.folder_monitor_frame = FolderMonitorFrame(app=self.app_context)
        self.regex_management_frame = RegexManagementFrame(app=self.app_context)
        self.override_names_frame = OverrideNamesFrame(app=self.app_context)
        self.image_trans_frame = ImageTransFrame(app=self.app_context)  # 기존의 새로운 프레임 추가
        self.upload_data_frame = UploadDataFrame(app=self.app_context)  # 새로 추가된 UploadDataFrame
        self.monitoring_controls = MonitoringControls(parent=self, app=self)

        self.tabs.addTab(self.folder_monitor_frame, "Monitor Settings")
        self.tabs.addTab(self.regex_management_frame, "Regex")
        self.tabs.addTab(self.override_names_frame, "Override Names")
        self.tabs.addTab(self.image_trans_frame, "Image Trans")  # 기존의 새로운 탭 추가
        self.tabs.addTab(self.upload_data_frame, "Upload Data")  # 새로 추가된 탭

        layout.addWidget(self.tabs)
        layout.addWidget(self.monitoring_controls)

        # Set initial value for base_date_combo from settings
        self.override_names_frame.base_date_combo.setCurrentText(self.app_context.base_date_folder)

        self.tray_icon = run_tray_icon(self)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def start_monitoring(self):
        self.monitoring_controls.start_monitoring()

    def stop_monitoring(self):
        self.monitoring_controls.stop_monitoring()

    def quit_app(self):
        self.monitoring_controls.quit_app()

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()

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

    def show_window(self):
        self.show()
        self.activateWindow()
