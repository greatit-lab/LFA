import os
from datetime import datetime
from utils import normalize_path, get_log_file_size

class EventLogger:
    def __init__(self, base_dir):
        self.log_dir_path = normalize_path(base_dir)
        os.makedirs(self.log_dir_path, exist_ok=True)
        self.current_date = datetime.now().strftime('%Y%m%d')
        self.log_file_base_name = f"{self.current_date}_event.log"
        self.debug_log_file_base_name = f"{self.current_date}_debug.log"
        self.log_file_path = os.path.join(self.log_dir_path, self.log_file_base_name)
        self.debug_log_file_path = os.path.join(self.log_dir_path, self.debug_log_file_base_name)
        self.debug_mode = False

    def _update_log_file_path(self):
        new_date = datetime.now().strftime('%Y%m%d')
        if new_date != self.current_date:
            self.current_date = new_date
            self.log_file_base_name = f"{self.current_date}_event.log"
            self.debug_log_file_base_name = f"{self.current_date}_debug.log"
            self.log_file_path = os.path.join(self.log_dir_path, self.log_file_base_name)
            self.debug_log_file_path = os.path.join(self.log_dir_path, self.debug_log_file_base_name)

    def _rotate_log_file(self, file_path, base_name):
        if get_log_file_size(file_path) >= 5 * 1024 * 1024:  # 5MB
            base, ext = os.path.splitext(base_name)
            counter = 1
            new_file_path = os.path.join(self.log_dir_path, f"{base}_{counter}{ext}")
            while os.path.exists(new_file_path):
                counter += 1
                new_file_path = os.path.join(self.log_dir_path, f"{base}_{counter}{ext}")
            os.rename(file_path, new_file_path)

    def log_event(self, event_type, src_path, dest_path=None):
        self._update_log_file_path()
        self._rotate_log_file(self.log_file_path, self.log_file_base_name)
        src_path = normalize_path(src_path)
        if dest_path:
            dest_path = normalize_path(dest_path)
        if self.log_file_path:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            with open(self.log_file_path, 'a', encoding='utf-8') as log_file:
                if event_type == "Created":
                    if dest_path:
                        dest_folder_path = os.path.dirname(dest_path)
                        log_file.write(f"{timestamp} - File Created: {src_path} -> copied to: {dest_folder_path}\n")
                    else:
                        log_file.write(f"{timestamp} - File Created: {src_path}\n")
                elif event_type == "Renamed":
                    if dest_path:
                        dest_filename = os.path.basename(dest_path)
                        log_file.write(f"{timestamp} - File Renamed: {src_path} -> {dest_filename}\n")
                    else:
                        log_file.write(f"{timestamp} - File Renamed: {src_path}\n")
                elif event_type == "Comparison and Replacement":
                    log_file.write(f"{timestamp} - File Comparison and Replacement: {src_path}\n")
                else:
                    if dest_path:
                        dest_folder_path = os.path.dirname(dest_path)
                        log_file.write(f"{timestamp} - {event_type}: {src_path} -> copied to: {dest_folder_path}\n")
                    else:
                        log_file.write(f"{timestamp} - {event_type}: {src_path}\n")

    def log_debug(self, message):
        self._update_log_file_path()
        self._rotate_log_file(self.debug_log_file_path, self.debug_log_file_base_name)
        if self.debug_log_file_path and self.debug_mode:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            with open(self.debug_log_file_path, 'a', encoding='utf-8') as debug_log_file:
                debug_log_file.write(f"{timestamp} - DEBUG: {message}\n")

    def set_debug_mode(self, debug_mode):
        self.debug_mode = debug_mode
        self.log_debug(f"Debug mode enabled: {self.debug_mode}")
