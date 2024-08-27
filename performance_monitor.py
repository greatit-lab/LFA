import psutil  # 시스템 및 프로세스 유틸리티를 제공하는 라이브러리
from datetime import datetime  # 날짜와 시간을 처리하는 모듈
import os  # 운영체제와 상호작용하기 위한 모듈
from utils import normalize_path, get_log_file_size  # 경로 정규화 및 파일 크기 확인을 위한 유틸리티 함수

class PerformanceMonitor:
    # 시스템 성능(예: CPU 및 메모리 사용량)을 모니터링하고 로그로 기록하는 클래스입니다.
    def __init__(self, base_dir):
        # 로그를 저장할 디렉토리 경로를 설정합니다.
        self.log_dir = normalize_path(base_dir)
        # 로그 디렉토리가 존재하지 않으면 생성합니다.
        os.makedirs(self.log_dir, exist_ok=True)
        # 현재 날짜를 'YYYYMMDD' 형식으로 설정합니다.
        self.current_date = datetime.now().strftime('%Y%m%d')
        # 성능 로그 파일의 기본 이름을 설정합니다.
        self.log_file_base_name = f"{self.current_date}_performance.log"
        # 로그 파일의 경로를 설정합니다.
        self.log_file_path = os.path.join(self.log_dir, self.log_file_base_name)

    def _update_log_file_path(self):
        # 날짜가 변경되었는지 확인하여 로그 파일 경로를 업데이트합니다.
        new_date = datetime.now().strftime('%Y%m%d')
        if new_date != self.current_date:
            self.current_date = new_date
            self.log_file_base_name = f"{self.current_date}_performance.log"
            self.log_file_path = os.path.join(self.log_dir, self.log_file_base_name)

    def _rotate_log_file(self, file_path, base_name):
        # 로그 파일의 크기가 5MB 이상인 경우, 파일을 회전(백업)합니다.
        if get_log_file_size(file_path) >= 5 * 1024 * 1024:  # 5MB
            base, ext = os.path.splitext(base_name)
            counter = 1
            # 동일한 이름의 파일이 이미 존재할 경우, 숫자를 증가시켜 새 이름을 만듭니다.
            new_file_path = os.path.join(self.log_dir, f"{base}_{counter}{ext}")
            while os.path.exists(new_file_path):
                counter += 1
                new_file_path = os.path.join(self.log_dir, f"{base}_{counter}{ext}")
            # 오래된 로그 파일을 새 이름으로 변경합니다.
            os.rename(file_path, new_file_path)

    def log_performance(self):
        # 현재 시스템의 성능 정보를 로그 파일에 기록합니다.
        self._update_log_file_path()
        self._rotate_log_file(self.log_file_path, self.log_file_base_name)
        with open(self.log_file_path, 'a', encoding='utf-8') as log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            # CPU 사용량과 메모리 사용량을 얻습니다.
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            # 성능 정보를 로그 파일에 기록합니다.
            log_file.write(f"{timestamp} - PerformanceMonitor: CPU Usage: {cpu_usage}%, Memory Usage: {memory_info.percent}%\n")
