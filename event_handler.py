import os
from datetime import datetime
from utils import normalize_path, get_log_file_size

class EventLogger:
    # EventLogger 클래스는 파일 이벤트와 디버그 메시지를 기록하는 역할을 합니다.
    def __init__(self, base_dir):
        # 로그를 저장할 디렉토리 경로를 설정합니다.
        self.log_dir_path = normalize_path(base_dir)
        # 로그 디렉토리가 존재하지 않으면 생성합니다.
        os.makedirs(self.log_dir_path, exist_ok=True)
        # 현재 날짜를 'YYYYMMDD' 형식으로 설정합니다.
        self.current_date = datetime.now().strftime('%Y%m%d')
        # 이벤트 로그와 디버그 로그의 파일 이름을 설정합니다.
        self.log_file_base_name = f"{self.current_date}_event.log"
        self.debug_log_file_base_name = f"{self.current_date}_debug.log"
        # 로그 파일 경로를 설정합니다.
        self.log_file_path = os.path.join(self.log_dir_path, self.log_file_base_name)
        self.debug_log_file_path = os.path.join(self.log_dir_path, self.debug_log_file_base_name)
        # 디버그 모드를 초기화합니다. (초기값은 False)
        self.debug_mode = False

    def _update_log_file_path(self):
        # 날짜가 변경되었는지 확인하여 로그 파일 경로를 업데이트합니다.
        new_date = datetime.now().strftime('%Y%m%d')
        if new_date != self.current_date:
            self.current_date = new_date
            self.log_file_base_name = f"{self.current_date}_event.log"
            self.debug_log_file_base_name = f"{self.current_date}_debug.log"
            self.log_file_path = os.path.join(self.log_dir_path, self.log_file_base_name)
            self.debug_log_file_path = os.path.join(self.log_dir_path, self.debug_log_file_base_name)

    def _rotate_log_file(self, file_path, base_name):
        # 로그 파일의 크기가 5MB 이상인 경우, 파일을 회전(백업)합니다.
        if get_log_file_size(file_path) >= 5 * 1024 * 1024:  # 5MB
            base, ext = os.path.splitext(base_name)
            counter = 1
            # 로그 파일이 이미 존재할 경우, 숫자를 증가시켜 새 이름을 만듭니다.
            new_file_path = os.path.join(self.log_dir_path, f"{base}_{counter}{ext}")
            while os.path.exists(new_file_path):
                counter += 1
                new_file_path = os.path.join(self.log_dir_path, f"{base}_{counter}{ext}")
            # 오래된 로그 파일을 새 이름으로 변경합니다.
            os.rename(file_path, new_file_path)

    def log_event(self, event_type, src_path, dest_path=None):
        # 로그 파일 경로를 갱신하고, 로그 파일 회전을 처리한 후 이벤트를 기록합니다.
        self._update_log_file_path()
        self._rotate_log_file(self.log_file_path, self.log_file_base_name)
        # 경로를 정규화합니다. (운영체제에 맞는 경로 형태로 변경)
        src_path = normalize_path(src_path)
        if dest_path:
            dest_path = normalize_path(dest_path)
        # 이벤트를 로그 파일에 기록합니다.
        if self.log_file_path:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            with open(self.log_file_path, 'a', encoding='utf-8') as log_file:
                if event_type == "Created":
                    if dest_path:
                        dest_folder_path = os.path.dirname(dest_path)
                        log_file.write(f"{timestamp} - event_handler: File Created: {src_path} -> copied to: {dest_folder_path}\n")
                    else:
                        log_file.write(f"{timestamp} - event_handler: File Created: {src_path}\n")
                elif event_type == "Renamed":
                    if dest_path:
                        dest_filename = os.path.basename(dest_path)
                        log_file.write(f"{timestamp} - event_handler: File Renamed: {src_path} -> {dest_filename}\n")
                    else:
                        log_file.write(f"{timestamp} - event_handler: File Renamed: {src_path}\n")
                elif event_type == "Comparison and Replacement":
                    log_file.write(f"{timestamp} - event_handler: File Comparison and Replacement: {src_path}\n")
                else:
                    if dest_path:
                        dest_folder_path = os.path.dirname(dest_path)
                        log_file.write(f"{timestamp} - event_handler: {event_type}: {src_path} -> copied to: {dest_folder_path}\n")
                    else:
                        log_file.write(f"{timestamp} - event_handler: {event_type}: {src_path}\n")

    def log_debug(self, message):
        # 디버그 메시지를 기록합니다. 디버그 모드가 활성화된 경우에만 동작합니다.
        self._update_log_file_path()
        self._rotate_log_file(self.debug_log_file_path, self.debug_log_file_base_name)
        if self.debug_log_file_path and self.debug_mode:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            with open(self.debug_log_file_path, 'a', encoding='utf-8') as debug_log_file:
                debug_log_file.write(f"{timestamp} - event_handler: DEBUG: {message}\n")

    def set_debug_mode(self, debug_mode):
        # 디버그 모드를 설정합니다. (True 또는 False)
        self.debug_mode = debug_mode
        self.log_debug(f"event_handler: Debug mode enabled: {self.debug_mode}")
