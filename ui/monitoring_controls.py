from PySide6.QtWidgets import QWidget, QPushButton, QCheckBox, QHBoxLayout, QVBoxLayout, QLabel, QApplication, QMessageBox
from PySide6.QtCore import Qt
from threading import Thread
from file_monitor.start_monitoring import start_monitoring
from config import save_settings

class MonitoringControls(QWidget):
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.status_label = QLabel("Status: Idle")
        layout.addWidget(self.status_label)

        self.run_button = QPushButton("Run")
        self.stop_button = QPushButton("Stop")
        self.quit_button = QPushButton("Quit")
        self.debug_checkbox = QCheckBox("Debug Mode")

        self.run_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.quit_button.clicked.connect(self.quit_app)
        self.debug_checkbox.stateChanged.connect(self.toggle_debug_mode)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.quit_button)
        button_layout.addWidget(self.debug_checkbox)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.stop_button.setEnabled(False)

    def start_monitoring(self):
        if not self.app:
            print("App context is not set.")
            return

        # Save the selected folder in the combo box to settings.ini
        self.app.app_context.base_date_folder = self.app.override_names_frame.base_date_combo.currentText()
        self.app.app_context.target_compare_folders = self.app.app_context.target_compare_folders
        self.app.app_context.save_settings()

        self.app.override_names_frame.base_date_clear_button.setEnabled(False)  # Disable the Clear button when monitoring starts
        self.app.override_names_frame.base_date_combo.setEnabled(False)  # Disable the combo box when monitoring starts
        self.app.override_names_frame.set_controls_enabled(False)  # Disable target compare path controls
        self.app.regex_management_frame.set_controls_enabled(False)  # Disable regex management controls
        self.app.folder_monitor_frame.set_controls_enabled(False)  # Disable folder monitoring controls
        self.debug_checkbox.setEnabled(False)  # Disable debug checkbox when monitoring starts

        self.status_label.setText("Status: Monitoring")
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.app.logger.log_event("Monitoring started", "")
        self.app.stop_event.clear()
        self.monitoring_thread = Thread(target=start_monitoring, args=(self.app,))
        self.monitoring_thread.start()
        self.app.tray_icon.setToolTip("LogFusion Agent (Monitoring)")
        self.app.update_tray_menu()

    def stop_monitoring(self):
        if not self.app:
            print("App context is not set.")
            return

        self.status_label.setText("Status: Stopped")
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.app.logger.log_event("Monitoring stopped", "")
        self.app.stop_event.set()
        self.app.override_names_frame.base_date_combo.setEnabled(True)  # Enable the combo box when monitoring stops
        self.app.override_names_frame.base_date_clear_button.setEnabled(True)  # Enable the Clear button when monitoring stops
        self.app.override_names_frame.set_controls_enabled(True)  # Enable target compare path controls
        self.app.regex_management_frame.set_controls_enabled(True)  # Enable regex management controls
        self.app.folder_monitor_frame.set_controls_enabled(True)  # Enable folder monitoring controls
        self.debug_checkbox.setEnabled(True)  # Enable debug checkbox when monitoring stops

        self.app.tray_icon.setToolTip("LogFusion Agent (Stopped)")
        self.app.update_tray_menu()

    def quit_app(self):
        if not self.app:
            print("App context is not set.")
            return

        if self.status_label.text() not in ["Status: Stopped", "Status: Idle"]:
            QMessageBox.warning(self, "Warning", "Stop monitoring before quitting the application.")
            return

        self.app.stop_event.set()
        self.app.logger.log_event("Application quit", "")
        self.app.tray_icon.hide()
        QApplication.instance().quit()  # type: ignore

    def toggle_debug_mode(self, state):
        if not self.app:
            print("App context is not set.")
            return

        if state == Qt.Checked or state == 2:  # type: ignore
            self.app.logger.set_debug_mode(True)
        elif state == Qt.Unchecked or state == 0:  # type: ignore
            self.app.logger.set_debug_mode(False)

        if self.app.logger.debug_mode:
            self.app.logger.log_debug("Debug mode enabled.")
        else:
            self.app.logger.log_debug("Debug mode disabled.")
