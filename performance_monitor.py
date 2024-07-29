import psutil
from datetime import datetime
import os
from utils import normalize_path, get_log_file_size

class PerformanceMonitor:
    def __init__(self, base_dir):
        self.log_dir = normalize_path(base_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        self.current_date = datetime.now().strftime('%Y%m%d')
        self.log_file_base_name = f"{self.current_date}_performance.log"
        self.log_file_path = os.path.join(self.log_dir, self.log_file_base_name)

    def _update_log_file_path(self):
        new_date = datetime.now().strftime('%Y%m%d')
        if new_date != self.current_date:
            self.current_date = new_date
            self.log_file_base_name = f"{self.current_date}_performance.log"
            self.log_file_path = os.path.join(self.log_dir, self.log_file_base_name)

    def _rotate_log_file(self, file_path, base_name):
        if get_log_file_size(file_path) >= 5 * 1024 * 1024:  # 5MB
            base, ext = os.path.splitext(base_name)
            counter = 1
            new_file_path = os.path.join(self.log_dir, f"{base}_{counter}{ext}")
            while os.path.exists(new_file_path):
                counter += 1
                new_file_path = os.path.join(self.log_dir, f"{base}_{counter}{ext}")
            os.rename(file_path, new_file_path)

    def log_performance(self):
        self._update_log_file_path()
        self._rotate_log_file(self.log_file_path, self.log_file_base_name)
        with open(self.log_file_path, 'a', encoding='utf-8') as log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            log_file.write(f"{timestamp} - PerformanceMonitor: CPU Usage: {cpu_usage}%, Memory Usage: {memory_info.percent}%\n")