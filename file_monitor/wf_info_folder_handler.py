import os
from datetime import datetime, timedelta
from watchdog.events import FileSystemEventHandler
from utils import normalize_path

class WfInfoFolderHandler(FileSystemEventHandler):
    def __init__(self, target_compare_folders, log_event, log_debug, event_queue, processed_events):
        self.target_compare_folders = [normalize_path(folder) for folder in target_compare_folders]
        self.log_event = log_event
        self.log_debug = log_debug
        self.event_queue = event_queue
        self.processed_events = processed_events
        self.debounce_time = timedelta(seconds=5)   # 디바운스 시간을 5초로 설정

    def on_created(self, event):
        if not event.is_directory and self.is_wf_info_folder(event.src_path):
            normalized_path = normalize_path(event.src_path)
            event_id = ('created', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('wf_info_created', normalized_path))
                self.log_debug(f"WfInfoFolderHandler: Created event detected for {normalized_path}")
            else:
                self.log_debug(f"WfInfoFolderHandler: Created event ignored for {normalized_path} due to debounce")

    def on_modified(self, event):
        if not event.is_directory and self.is_wf_info_folder(event.src_path):
            normalized_path = normalize_path(event.src_path)
            event_id = ('modified', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('wf_info_modified', normalized_path))
                self.log_debug(f"WfInfoFolderHandler: Modified event detected for {normalized_path}")
            else:
                self.log_debug(f"WfInfoFolderHandler: Modified event ignored for {normalized_path} due to debounce")

    def on_deleted(self, event):
        if not event.is_directory and self.is_wf_info_folder(event.src_path):
            normalized_path = normalize_path(event.src_path)
            event_id = ('deleted', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('deleted', normalized_path))
                self.log_debug(f"WfInfoFolderHandler: Deleted event detected for {normalized_path}")
            else:
                self.log_debug(f"WfInfoFolderHandler: Deleted event ignored for {normalized_path} due to debounce")

    def on_moved(self, event):
        if not event.is_directory and self.is_wf_info_folder(event.src_path):
            normalized_src_path = normalize_path(event.src_path)
            normalized_dest_path = normalize_path(event.dest_path)
            event_id = ('moved', normalized_src_path, normalized_dest_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('moved', normalized_src_path, normalized_dest_path))
                self.log_debug(f"WfInfoFolderHandler: Moved event detected from {normalized_src_path} to {normalized_dest_path}")
            else:
                self.log_debug(f"WfInfoFolderHandler: Moved event ignored from {normalized_src_path} to {normalized_dest_path} due to debounce")

    def is_wf_info_folder(self, path):
        return any(normalize_path(path).startswith(folder) for folder in self.target_compare_folders)
