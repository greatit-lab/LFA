import sys
import os
import psutil
from PySide6.QtWidgets import QApplication, QDialog
from ui.app import MonitorApp
from ui.eqpid_input import EqpidInputDialog
from config import load_settings, save_settings, load_eqpid, save_eqpid
from logger import setup_event_logging, add_debug_logging, update_logging_config

class AppContext:
    def __init__(self, base_dir):
        self.eqpid = load_eqpid()  # Load EQPID
        self.monitored_folders, self.dest_folder, self.regex_folders, self.exclude_folders, self.base_date_folder, self.target_compare_folders, self.target_image_folder, self.wait_time, self.image_save_folder = load_settings()
        self.base_dir = base_dir
        self.logger = None

    def initialize_logger(self):
        if self.logger is None:
            setup_event_logging(self.base_dir)
            add_debug_logging(self.base_dir)

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
            self.image_save_folder
        )

def is_another_instance_running(pid_file):
    if os.path.isfile(pid_file):
        with open(pid_file, 'r') as f:
            pid = int(f.read())
        if psutil.pid_exists(pid):
            return True
        else:
            os.remove(pid_file)
    return False

def create_pid_file(pid_file):
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))

def remove_pid_file(pid_file):
    if os.path.isfile(pid_file):
        os.remove(pid_file)

if __name__ == "__main__":
    PID_FILE = 'program.pid'
    if is_another_instance_running(PID_FILE):
        print("Another instance of the program is already running.")
        sys.exit(1)
    create_pid_file(PID_FILE)

    app = QApplication(sys.argv)

    eqpid = load_eqpid()
    if eqpid is None:
        dialog = EqpidInputDialog()
        if dialog.exec_() == QDialog.Accepted:
            eqpid = dialog.get_eqpid()
            save_eqpid(eqpid)
        else:
            sys.exit(0)

    base_dir = os.path.join(os.getcwd(), 'EventLog')
    app_context = AppContext(base_dir)
    app_context.initialize_logger() # Initialize logger
    
    main_window = MonitorApp(app_context, base_dir)

    def on_close():
        app_context.save_settings()
        remove_pid_file(PID_FILE)
        sys.exit(0)

    app.aboutToQuit.connect(on_close)
    main_window.show()
    sys.exit(app.exec())