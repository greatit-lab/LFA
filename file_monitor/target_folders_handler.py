import os
from datetime import datetime, timedelta
from watchdog.events import FileSystemEventHandler
from utils import normalize_path

class TargetFoldersHandler(FileSystemEventHandler):
    def __init__(self, dest_folder, regex_folders, exclude_folders, log_event, log_debug, event_queue, processed_events):
        self.dest_folder = normalize_path(dest_folder)
        self.regex_folders = regex_folders
        self.exclude_folders = [normalize_path(folder) for folder in exclude_folders]
        self.log_event = log_event
        self.log_debug = log_debug
        self.event_queue = event_queue
        self.processed_events = processed_events
        self.debounce_time = timedelta(seconds=5)   # 디바운스 시간을 5초로 설정

    def on_created(self, event):
        if not event.is_directory and not self.is_excluded(event.src_path):
            normalized_path = normalize_path(event.src_path)
            event_id = ('created', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('created', normalized_path))
                self.log_debug(f"TargetFoldersHandler: Created event detected for {normalized_path}")
            else:
                self.log_debug(f"TargetFoldersHandler: Created event ignored for {normalized_path} due to debounce")

    def on_modified(self, event):
        if not event.is_directory and not self.is_excluded(event.src_path):
            normalized_path = normalize_path(event.src_path)
            event_id = ('modified', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('modified', normalized_path))
                self.log_debug(f"TargetFoldersHandler: Modified event detected for {normalized_path}")
            else:
                self.log_debug(f"TargetFoldersHandler: Modified event ignored for {normalized_path} due to debounce")

    def on_deleted(self, event):
        if not event.is_directory and not self.is_excluded(event.src_path):
            normalized_path = normalize_path(event.src_path)
            event_id = ('deleted', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('deleted', normalized_path))
                self.log_debug(f"TargetFoldersHandler: Deleted event detected for {normalized_path}")
            else:
                self.log_debug(f"TargetFoldersHandler: Deleted event ignored for {normalized_path} due to debounce")

    def on_moved(self, event):
        if not event.is_directory and not self.is_excluded(event.src_path):
            normalized_src_path = normalize_path(event.src_path)
            normalized_dest_path = normalize_path(event.dest_path)
            event_id = ('moved', normalized_src_path, normalized_dest_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > self.debounce_time:
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('moved', normalized_src_path, normalized_dest_path))
                self.log_debug(f"TargetFoldersHandler: Moved event detected from {normalized_src_path} to {normalized_dest_path}")
            else:
                self.log_debug(f"TargetFoldersHandler: Moved event ignored from {normalized_src_path} to {normalized_dest_path} due to debounce")

    def is_excluded(self, path):
        for folder in self.exclude_folders:
            if normalize_path(path).startswith(folder):
                return True
        return False
