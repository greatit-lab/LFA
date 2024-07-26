import os
from datetime import datetime, timedelta
from watchdog.events import FileSystemEventHandler
from utils import normalize_path
from file_monitor.event_processor import create_file_based_on_datetime

class BaseDateFolderHandler(FileSystemEventHandler):
    def __init__(self, base_date_folder, save_to_folder, log_event, log_debug, event_queue, processed_events):
        self.base_date_folder = normalize_path(base_date_folder)
        self.save_to_folder = normalize_path(save_to_folder)
        self.log_event = log_event
        self.log_debug = log_debug
        self.event_queue = event_queue
        self.processed_events = processed_events
        self.creation_times = {}
        self.debounce_time = timedelta(seconds=5)   # 디바운스 시간을 5초로 설정

    def on_created(self, event):
        if not event.is_directory:
            normalized_path = normalize_path(event.src_path)
            self.log_debug(f"BaseDateFolderHandler: on_created triggered for {normalized_path}")
            self.creation_times[normalized_path] = datetime.now()
            event_id = ('created', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                success = create_file_based_on_datetime(normalized_path, self.log_debug, self.log_event, self.save_to_folder)
                if success:
                    self.log_debug(f"BaseDateFolderHandler: File created based on datetime extraction from {normalized_path}")
            else:
                self.log_debug(f"BaseDateFolderHandler: Created event ignored for {normalized_path} due to debounce")

    def on_modified(self, event):
        if not event.is_directory:
            normalized_path = normalize_path(event.src_path)
            self.log_debug(f"BaseDateFolderHandler: on_modified triggered for {normalized_path}")
            if normalized_path in self.creation_times:
                creation_time = self.creation_times[normalized_path]
                if datetime.now() - creation_time < timedelta(seconds=1):
                    self.log_debug(f"BaseDateFolderHandler: Ignoring modified event for {normalized_path} immediately after creation")
                    return
            event_id = ('modified', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                success = create_file_based_on_datetime(normalized_path, self.log_debug, self.log_event, self.save_to_folder)
                self.event_queue.put(('base_date_modified', normalized_path, self.target_image_folder, self.wait_time, self.image_save_folder))
                if success:
                    self.log_debug(f"BaseDateFolderHandler: Modified event detected for {normalized_path}")
            else:
                self.log_debug(f"BaseDateFolderHandler: Modified event ignored for {normalized_path} due to debounce")

    def on_deleted(self, event):
        if not event.is_directory:
            normalized_path = normalize_path(event.src_path)
            event_id = ('deleted', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                
                self.log_event("File Deleted", normalized_path)
                self.log_debug(f"BaseDateFolderHandler: Deleted event detected for {normalized_path}")

    def on_moved(self, event):
        if not event.is_directory:
            normalized_src_path = normalize_path(event.src_path)
            normalized_dest_path = normalize_path(event.dest_path)
            event_id = ('moved', normalized_src_path, normalized_dest_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                
                self.log_event("File Moved", normalized_src_path, normalized_dest_path)
                self.log_debug(f"BaseDateFolderHandler: Moved event detected from {normalized_src_path} to {normalized_dest_path}")