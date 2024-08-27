import os
from datetime import datetime, timedelta
from watchdog.events import FileSystemEventHandler
from utils import normalize_path

# TargetFoldersHandler 클래스는 특정 폴더에서 발생하는 파일 시스템 이벤트를 감지하고 처리하는 역할을 합니다.
class TargetFoldersHandler(FileSystemEventHandler):
    def __init__(self, dest_folder, regex_folders, exclude_folders, log_event, log_debug, event_queue, processed_events):
        # 클래스 초기화 메서드입니다. 감시할 대상 폴더, 제외할 폴더, 로그 함수 등을 설정합니다.
        self.dest_folder = normalize_path(dest_folder)  # 대상 폴더 경로를 정규화합니다.
        self.regex_folders = {pattern: normalize_path(folder) for pattern, folder in regex_folders.items()}  # 정규 표현식과 폴더 경로를 매핑합니다.
        self.exclude_folders = [normalize_path(folder) for folder in exclude_folders]  # 제외할 폴더들을 정규화합니다.
        self.log_event = log_event  # 이벤트 로그를 기록하는 함수입니다.
        self.log_debug = log_debug  # 디버그 로그를 기록하는 함수입니다.
        self.event_queue = event_queue  # 발생한 이벤트를 처리하기 위한 큐입니다.
        self.processed_events = processed_events  # 이미 처리된 이벤트를 저장해 중복 처리를 방지합니다.
        self.creation_times = {}  # 파일이 생성된 시간을 기록합니다.

    # 특정 경로가 제외 폴더에 속하는지 확인하는 메서드입니다.
    def is_excluded(self, path):
        normalized_path = normalize_path(path)  # 경로를 정규화합니다.
        return any(normalized_path.startswith(exclude_folder) for exclude_folder in self.exclude_folders)  # 제외 폴더 중 하나에 속하면 True를 반환합니다.

    # 파일이나 폴더가 생성되었을 때 호출되는 메서드입니다.
    def on_created(self, event):
        if not event.is_directory and not self.is_excluded(event.src_path):  # 생성된 항목이 폴더가 아니고 제외되지 않은 경우
            normalized_path = normalize_path(event.src_path)  # 생성된 경로를 정규화합니다.
            self.creation_times[normalized_path] = datetime.now()  # 생성된 시간을 기록합니다.
            event_id = ('created', normalized_path)
            # 중복 이벤트를 방지하기 위해 처리 시간을 확인합니다.
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('created', normalized_path))  # 이벤트 큐에 '생성' 이벤트를 추가합니다.
                self.log_debug(f"TargetFoldersHandler: Created event detected for {normalized_path}")
            else:
                self.log_debug(f"TargetFoldersHandler: Created event ignored for {normalized_path} due to debounce")

    # 파일이나 폴더가 수정되었을 때 호출되는 메서드입니다.
    def on_modified(self, event):
        if not event.is_directory and not self.is_excluded(event.src_path):  # 수정된 항목이 폴더가 아니고 제외되지 않은 경우
            normalized_path = normalize_path(event.src_path)  # 수정된 경로를 정규화합니다.
            if normalized_path in self.creation_times:
                creation_time = self.creation_times[normalized_path]
                # 파일이 생성된 직후 수정된 경우, 이벤트를 무시합니다.
                if datetime.now() - creation_time < timedelta(seconds=1):
                    self.log_debug(f"TargetFoldersHandler: ignoring modified event for {normalized_path} immediately after creation")
                    return
            
            event_id = ('modified', normalized_path)
            # 중복 이벤트를 방지하기 위해 처리 시간을 확인합니다.
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('modified', normalized_path))  # 이벤트 큐에 '수정' 이벤트를 추가합니다.
                self.log_debug(f"TargetFoldersHandler: Modified event detected for {normalized_path}")
            else:
                self.log_debug(f"TargetFoldersHandler: Modified event ignored for {normalized_path} due to debounce")

    # 파일이나 폴더가 삭제되었을 때 호출되는 메서드입니다.
    def on_deleted(self, event):
        if not event.is_directory and not self.is_excluded(event.src_path):  # 삭제된 항목이 폴더가 아니고 제외되지 않은 경우
            normalized_path = normalize_path(event.src_path)  # 삭제된 경로를 정규화합니다.
            event_id = ('deleted', normalized_path)
            # 중복 이벤트를 방지하기 위해 처리 시간을 확인합니다.
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('deleted', normalized_path))  # 이벤트 큐에 '삭제' 이벤트를 추가합니다.
                self.log_debug(f"TargetFoldersHandler: Deleted event detected for {normalized_path}")
            else:
                self.log_debug(f"TargetFoldersHandler: Deleted event ignored for {normalized_path} due to debounce")

    # 파일이나 폴더가 이동되었을 때 호출되는 메서드입니다.
    def on_moved(self, event):
        if not event.is_directory and not self.is_excluded(event.src_path):  # 이동된 항목이 폴더가 아니고 제외되지 않은 경우
            normalized_src_path = normalize_path(event.src_path)  # 원본 경로를 정규화합니다.
            normalized_dest_path = normalize_path(event.dest_path)  # 이동된 경로를 정규화합니다.
            event_id = ('moved', normalized_src_path, normalized_dest_path)
            # 중복 이벤트를 방지하기 위해 처리 시간을 확인합니다.
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('moved', normalized_src_path, normalized_dest_path))  # 이벤트 큐에 '이동' 이벤트를 추가합니다.
                self.log_debug(f"TargetFoldersHandler: Moved event detected from {normalized_src_path} to {normalized_dest_path}")
            else:
                self.log_debug(f"TargetFoldersHandler: Moved event ignored from {normalized_src_path} to {normalized_dest_path} due to debounce")
