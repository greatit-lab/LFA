from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def run_tray_icon(app):
    icon_path = resource_path("resources/icons/icon.png")
    tray_icon = QSystemTrayIcon(QIcon(icon_path), app)
    tray_icon.setToolTip("LogFusion Agent")

    def show_window():
        app.show_window()

    def start_monitoring():
        app.start_monitoring()
        update_tray_menu()

    def stop_monitoring():
        app.stop_monitoring()
        update_tray_menu()

    def quit_app():
        app.quit_app()

    def update_tray_menu():
        menu.clear()
        show_action = menu.addAction("Show")
        show_action.triggered.connect(show_window)
        run_action = menu.addAction("Run")
        run_action.setEnabled(app.monitoring_controls.status_label.text() in ["Status: Idle", "Status: Stopped"])
        run_action.triggered.connect(start_monitoring)
        stop_action = menu.addAction("Stop")
        stop_action.setEnabled(app.monitoring_controls.status_label.text() == "Status: Monitoring")
        stop_action.triggered.connect(stop_monitoring)
        quit_action = menu.addAction("Quit")
        quit_action.setEnabled(app.monitoring_controls.status_label.text() in ["Status: Idle", "Status: Stopped"])
        quit_action.triggered.connect(quit_app)
        tray_icon.setContextMenu(menu)

    menu = QMenu()
    update_tray_menu()
    tray_icon.setContextMenu(menu)
    tray_icon.show()
    return tray_icon