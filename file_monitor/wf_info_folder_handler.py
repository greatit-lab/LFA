import os
from datetime import datetime, timedelta
from watchdog.events import FileSystemEventHandler
from utils import normalize_path
from file_monitor.event_processor import extract_file_info, replace_text_in_files

class WfInfoFolderHandler(FileSystemEventHandler):
    def __init__(self, target_compare_folders, log_event, log_debug, event_queue, processed_events):
        self.target_compare_folders = [normalize_path(folder) for folder in target_compare_folders]
        self.log_event = log_event
        self.log_debug = log_debug
        self.event_queue = event_queue
        self.processed_events = processed_events
        self.creation_times = {}

    def on_created(self, event):
        if not event.is_directory:
            normalized_path = normalize_path(event.src_path)
            self.creation_times[normalized_path] = datetime.now()
            event_id = ('created', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('created', normalized_path))
                self.log_debug(f"Created event detected for {normalized_path}")

                wf_file_info = extract_file_info(os.path.basename(normalized_path))
                if wf_file_info[0] and wf_file_info[1] and wf_file_info[2]:
                    for target_folder in self.target_compare_folders:
                        replace_text_in_files(wf_file_info, target_folder, self.log_debug, self.log_event)
                        self.log_event("File Comparison and Replacement", f"Processed file: {normalized_path} with target folder: {target_folder}")

    def on_modified(self, event):
        if not event.is_directory:
            normalized_path = normalize_path(event.src_path)
            if normalized_path in self.creation_times:
                creation_time = self.creation_times[normalized_path]
                if datetime.now() - creation_time < timedelta(seconds=1):
                    self.log_debug(f"Ignoring modified event for {normalized_path} immediately after creation")
                    return
            event_id = ('modified', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('modified', normalized_path))
                self.log_debug(f"Modified event detected for {normalized_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            normalized_path = normalize_path(event.src_path)
            event_id = ('deleted', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('deleted', normalized_path))
                self.log_debug(f"Deleted event detected for {normalized_path}")

    def on_moved(self, event):
        if not event.is_directory:
            normalized_src_path = normalize_path(event.src_path)
            normalized_dest_path = normalize_path(event.dest_path)
            event_id = ('moved', normalized_src_path, normalized_dest_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('moved', normalized_src_path, normalized_dest_path))
                self.log_debug(f"Moved event detected from {normalized_src_path} to {normalized_dest_path}")
