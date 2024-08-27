import os  # 운영체제와 상호작용하기 위한 모듈
from datetime import datetime, timedelta  # 날짜와 시간을 처리하기 위한 모듈
from watchdog.events import FileSystemEventHandler  # 파일 시스템 이벤트를 처리하기 위한 watchdog 모듈의 클래스
from utils import normalize_path  # 경로를 정규화하기 위한 유틸리티 함수
from file_monitor.event_processor import create_file_based_on_datetime  # 파일을 처리하는 데 필요한 함수

# BaseDateFolderHandler 클래스는 특정 폴더에서 발생하는 파일 시스템 이벤트를 처리합니다.
class BaseDateFolderHandler(FileSystemEventHandler):
    def __init__(self, base_date_folder, save_to_folder, log_event, log_debug, event_queue, processed_events):
        # 폴더 경로와 이벤트 로그, 디버그 로그를 저장할 메서드를 초기화합니다.
        self.base_date_folder = normalize_path(base_date_folder)  # 기본 날짜 폴더의 경로를 정규화합니다.
        self.save_to_folder = normalize_path(save_to_folder)  # 저장할 폴더의 경로를 정규화합니다.
        self.log_event = log_event  # 이벤트 로깅 메서드
        self.log_debug = log_debug  # 디버그 로깅 메서드
        self.event_queue = event_queue  # 이벤트 큐
        self.processed_events = processed_events  # 이미 처리된 이벤트를 저장하는 딕셔너리
        self.creation_times = {}  # 파일 생성 시간을 저장하는 딕셔너리
        self.debounce_time = timedelta(seconds=5)  # 디바운스 시간을 5초로 설정합니다.

    def on_created(self, event):
        # 파일이 생성되었을 때 호출되는 메서드입니다.
        if not event.is_directory:
            normalized_path = normalize_path(event.src_path)  # 생성된 파일의 경로를 정규화합니다.
            self.log_debug(f"BaseDateFolderHandler: on_created triggered for {normalized_path}")
            self.creation_times[normalized_path] = datetime.now()  # 파일 생성 시간을 기록합니다.
            event_id = ('created', normalized_path)
            # 이벤트가 디바운스 시간 내에 발생하지 않았으면 처리합니다.
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                # 파일을 처리하는 함수를 호출하여 성공 여부를 확인합니다.
                success = create_file_based_on_datetime(normalized_path, self.log_debug, self.log_event, self.save_to_folder)
                if success:
                    self.log_debug(f"BaseDateFolderHandler: File created based on datetime extraction from {normalized_path}")
            else:
                self.log_debug(f"BaseDateFolderHandler: Created event ignored for {normalized_path} due to debounce")

    def on_modified(self, event):
        # 파일이 수정되었을 때 호출되는 메서드입니다.
        if not event.is_directory:
            normalized_path = normalize_path(event.src_path)  # 수정된 파일의 경로를 정규화합니다.
            self.log_debug(f"BaseDateFolderHandler: on_modified triggered for {normalized_path}")
            if normalized_path in self.creation_times:
                creation_time = self.creation_times[normalized_path]
                # 파일이 생성된 직후에 수정된 경우, 이 이벤트를 무시합니다.
                if datetime.now() - creation_time < timedelta(seconds=1):
                    self.log_debug(f"BaseDateFolderHandler: Ignoring modified event for {normalized_path} immediately after creation")
                    return
            event_id = ('modified', normalized_path)
            # 이벤트가 디바운스 시간 내에 발생하지 않았으면 처리합니다.
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                # 파일을 처리하는 함수를 호출하여 성공 여부를 확인합니다.
                success = create_file_based_on_datetime(normalized_path, self.log_debug, self.log_event, self.save_to_folder)
                if success:
                    self.log_debug(f"BaseDateFolderHandler: Modified event detected for {normalized_path}")
            else:
                self.log_debug(f"BaseDateFolderHandler: Modified event ignored for {normalized_path} due to debounce")

    def on_deleted(self, event):
        # 파일이 삭제되었을 때 호출되는 메서드입니다.
        if not event.is_directory:
            normalized_path = normalize_path(event.src_path)  # 삭제된 파일의 경로를 정규화합니다.
            event_id = ('deleted', normalized_path)
            # 이벤트가 디바운스 시간 내에 발생하지 않았으면 처리합니다.
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                # 삭제된 파일에 대한 이벤트를 기록합니다.
                self.log_event("File Deleted", normalized_path)
                self.log_debug(f"BaseDateFolderHandler: Deleted event detected for {normalized_path}")

    def on_moved(self, event):
        # 파일이 이동되었을 때 호출되는 메서드입니다.
        if not event.is_directory:
            normalized_src_path = normalize_path(event.src_path)  # 이동된 파일의 원래 경로를 정규화합니다.
            normalized_dest_path = normalize_path(event.dest_path)  # 이동된 파일의 새로운 경로를 정규화합니다.
            event_id = ('moved', normalized_src_path, normalized_dest_path)
            # 이벤트가 디바운스 시간 내에 발생하지 않았으면 처리합니다.
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                # 파일 이동에 대한 이벤트를 기록합니다.
                self.log_event("File Moved", normalized_src_path, normalized_dest_path)
                self.log_debug(f"BaseDateFolderHandler: Moved event detected from {normalized_src_path} to {normalized_dest_path}")
