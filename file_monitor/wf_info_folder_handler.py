import os
from datetime import datetime, timedelta
from watchdog.events import FileSystemEventHandler
from utils import normalize_path
from file_monitor.event_processor import process_images, replace_text_in_files, extract_file_info

# WfInfoFolderHandler 클래스는 wf_info 폴더에서 발생하는 파일 시스템 이벤트를 처리합니다.
# 이 클래스는 파일이 생성, 수정, 삭제, 이동될 때마다 호출되는 메서드를 정의합니다.
class WfInfoFolderHandler(FileSystemEventHandler):
    
    # 생성자 메서드: 클래스의 인스턴스를 초기화합니다.
    def __init__(self, target_image_folder, wait_time, image_save_folder, log_event, log_debug, event_queue, processed_events):
        # target_image_folder: 처리할 이미지 파일들이 있는 폴더 경로
        # wait_time: 이미지 처리 전에 대기할 시간
        # image_save_folder: 이미지가 저장될 폴더 경로
        # log_event: 이벤트를 기록하기 위한 함수
        # log_debug: 디버그 메시지를 기록하기 위한 함수
        # event_queue: 이벤트를 처리하기 위한 큐
        # processed_events: 이미 처리된 이벤트를 저장하는 딕셔너리
        self.target_image_folder = normalize_path(target_image_folder)
        self.wait_time = int(wait_time)
        self.image_save_folder = normalize_path(image_save_folder)
        self.log_event = log_event
        self.log_debug = log_debug
        self.event_queue = event_queue
        self.processed_events = processed_events
        self.creation_times = {}  # 파일 생성 시간을 저장하는 딕셔너리

    # 파일이 생성될 때 호출되는 메서드
    def on_created(self, event):
        if not event.is_directory:  # 이벤트가 디렉토리가 아닌 경우
            normalized_path = normalize_path(event.src_path)
            self.creation_times[normalized_path] = datetime.now()
            event_id = ('created', normalized_path)
            # 이전에 처리된 이벤트가 아니거나 일정 시간이 지난 경우 이벤트 처리
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                # 이벤트 큐에 생성 이벤트를 추가
                self.event_queue.put(('wf_info_created', normalized_path, self.target_image_folder, self.wait_time, self.image_save_folder))
                self.log_debug(f"WfInfoFolderHandler: Created event detected for {normalized_path}")

                # 파일 이름에서 특정 정보를 추출하여 다른 파일의 텍스트를 대체하는 함수 호출
                wf_file_info = extract_file_info(os.path.basename(normalized_path))
                if wf_file_info[0] and wf_file_info[1] and wf_file_info[2]:
                    replace_text_in_files(wf_file_info, self.target_image_folder, self.log_debug, self.log_event)

    # 파일이 수정될 때 호출되는 메서드
    def on_modified(self, event):
        if not event.is_directory:  # 이벤트가 디렉토리가 아닌 경우
            normalized_path = normalize_path(event.src_path)
            # 파일이 생성된 직후의 수정 이벤트는 무시
            if normalized_path in self.creation_times:
                creation_time = self.creation_times[normalized_path]
                if datetime.now() - creation_time < timedelta(seconds=1):
                    self.log_debug(f"WfInfoFolderHandler: Ignoring modified event for {normalized_path} immediately after creation")
                    return
            event_id = ('modified', normalized_path)
            # 이전에 처리된 이벤트가 아니거나 일정 시간이 지난 경우 이벤트 처리
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                # 이벤트 큐에 수정 이벤트를 추가
                self.event_queue.put(('wf_info_modified', normalized_path, self.target_image_folder, self.wait_time, self.image_save_folder))
                self.log_debug(f"WfInfoFolderHandler: Modified event detected for {normalized_path}")

    # 파일이 삭제될 때 호출되는 메서드
    def on_deleted(self, event):
        if not event.is_directory:  # 이벤트가 디렉토리가 아닌 경우
            normalized_path = normalize_path(event.src_path)
            event_id = ('deleted', normalized_path)
            # 이전에 처리된 이벤트가 아니거나 일정 시간이 지난 경우 이벤트 처리
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                # 삭제 이벤트를 기록
                self.log_event("File Deleted", normalized_path)
                self.log_debug(f"WfInfoFolderHandler: Deleted event detected for {normalized_path}")

    # 파일이 이동될 때 호출되는 메서드
    def on_moved(self, event):
        if not event.is_directory:  # 이벤트가 디렉토리가 아닌 경우
            normalized_src_path = normalize_path(event.src_path)
            normalized_dest_path = normalize_path(event.dest_path)
            event_id = ('moved', normalized_src_path, normalized_dest_path)
            # 이전에 처리된 이벤트가 아니거나 일정 시간이 지난 경우 이벤트 처리
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                # 이동 이벤트를 기록
                self.log_event("File Moved", normalized_src_path, normalized_dest_path)
                self.log_debug(f"WfInfoFolderHandler: Moved event detected from {normalized_src_path} to {normalized_dest_path}")
