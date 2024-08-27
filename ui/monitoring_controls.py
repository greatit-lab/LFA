from PySide6.QtWidgets import QWidget, QPushButton, QCheckBox, QHBoxLayout, QVBoxLayout, QLabel, QApplication, QMessageBox
from PySide6.QtCore import Qt
from threading import Thread
from file_monitor.start_monitoring import start_monitoring
from config import save_settings

class MonitoringControls(QWidget):
    def __init__(self, parent=None, app=None):
        # 모니터링 제어 UI를 초기화하고 애플리케이션 컨텍스트를 설정합니다.
        super().__init__(parent)
        self.app = app
        self.initUI()

    def initUI(self):
        # UI 레이아웃을 설정하고 각종 버튼 및 레이블을 배치합니다.
        layout = QVBoxLayout()
        self.status_label = QLabel("Status: Idle")  # 현재 상태를 나타내는 레이블
        layout.addWidget(self.status_label)

        self.run_button = QPushButton("Run")  # 모니터링 시작 버튼
        self.stop_button = QPushButton("Stop")  # 모니터링 중지 버튼
        self.quit_button = QPushButton("Quit")  # 애플리케이션 종료 버튼
        self.debug_checkbox = QCheckBox("Debug Mode")  # 디버그 모드 활성화 체크박스

        # 버튼 클릭 시 실행될 함수들을 연결합니다.
        self.run_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.quit_button.clicked.connect(self.quit_app)
        self.debug_checkbox.stateChanged.connect(self.toggle_debug_mode)

        # 버튼들을 레이아웃에 추가합니다.
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.quit_button)
        button_layout.addWidget(self.debug_checkbox)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # 처음에는 'Stop' 버튼을 비활성화 상태로 둡니다.
        self.stop_button.setEnabled(False)

    def start_monitoring(self):
        # 모니터링을 시작하고 UI를 업데이트합니다.
        if not self.app:
            print("App context is not set.")
            return

        # 사용자가 선택한 폴더 설정을 저장합니다.
        self.app.app_context.base_date_folder = self.app.override_names_frame.base_date_combo.currentText()
        self.app.app_context.target_compare_folders = self.app.app_context.target_compare_folders
        self.app.app_context.save_settings()

        # 모니터링 중에는 여러 UI 요소들을 비활성화합니다.
        self.app.override_names_frame.base_date_clear_button.setEnabled(False)
        self.app.override_names_frame.base_date_combo.setEnabled(False)
        self.app.override_names_frame.set_controls_enabled(False)
        self.app.regex_management_frame.set_controls_enabled(False)
        self.app.folder_monitor_frame.set_controls_enabled(False)
        self.app.image_trans_frame.set_controls_enabled(False)
        self.app.upload_data_frame.set_controls_enabled(False)
        self.debug_checkbox.setEnabled(False)

        # 상태를 'Monitoring'으로 설정하고, 버튼 상태를 업데이트합니다.
        self.status_label.setText("Status: Monitoring")
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.app.logger.log_event("Monitoring started", "")
        self.app.stop_event.clear()

        # 모니터링을 별도의 스레드에서 실행합니다.
        self.monitoring_thread = Thread(target=start_monitoring, args=(self.app,))
        self.monitoring_thread.start()
        self.app.tray_icon.setToolTip("LogFusion Agent (Monitoring)")
        self.app.update_tray_menu()

    def stop_monitoring(self):
        # 모니터링을 중지하고 UI를 업데이트합니다.
        if not self.app:
            print("App context is not set.")
            return

        # 상태를 'Stopped'로 설정하고, 버튼 상태를 업데이트합니다.
        self.status_label.setText("Status: Stopped")
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.app.logger.log_event("Monitoring stopped", "")
        self.app.stop_event.set()

        # 모니터링 중에 비활성화했던 UI 요소들을 다시 활성화합니다.
        self.app.override_names_frame.base_date_combo.setEnabled(True)
        self.app.override_names_frame.base_date_clear_button.setEnabled(True)
        self.app.override_names_frame.set_controls_enabled(True)
        self.app.regex_management_frame.set_controls_enabled(True)
        self.app.folder_monitor_frame.set_controls_enabled(True)
        self.app.image_trans_frame.set_controls_enabled(True)
        self.app.upload_data_frame.set_controls_enabled(True)
        self.debug_checkbox.setEnabled(True)

        self.app.tray_icon.setToolTip("LogFusion Agent (Stopped)")
        self.app.update_tray_menu()

    def quit_app(self):
        # 애플리케이션을 종료하기 전 필요한 작업을 처리합니다.
        if not self.app:
            print("App context is not set.")
            return

        # 모니터링 중인 상태에서는 종료할 수 없도록 합니다.
        if self.status_label.text() not in ["Status: Stopped", "Status: Idle"]:
            QMessageBox.warning(self, "Warning", "Stop monitoring before quitting the application.")
            return

        self.app.stop_event.set()
        self.app.logger.log_event("Application quit", "")
        self.app.tray_icon.hide()
        QApplication.instance().quit()  # type: ignore  # 애플리케이션을 종료합니다.

    def toggle_debug_mode(self, state):
        # 디버그 모드를 활성화하거나 비활성화합니다.
        if not self.app:
            print("App context is not set.")
            return

        # 체크박스 상태에 따라 디버그 모드를 설정합니다.
        if state == Qt.Checked or state == 2:   # type: ignore
            self.app.logger.set_debug_mode(True)
        elif state == Qt.Unchecked or state == 0:   # type: ignore
            self.app.logger.set_debug_mode(False)

        # 디버그 모드 활성화/비활성화에 따라 로그를 남깁니다.
        if self.app.logger.debug_mode:
            self.app.logger.log_debug("Debug mode enabled.")
        else:
            self.app.logger.log_debug("Debug mode disabled.")
