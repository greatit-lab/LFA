import os
from datetime import datetime, timedelta
from watchdog.events import FileSystemEventHandler
from utils import normalize_path
from file_monitor.event_processor import process_images, replace_text_in_files, extract_file_info

class WfInfoFolderHandler(FileSystemEventHandler):
    def __init__(self, target_image_folder, wait_time, image_save_folder, log_event, log_debug, event_queue, processed_events):
        self.target_image_folder = normalize_path(target_image_folder)
        self.wait_time = int(wait_time)
        self.image_save_folder = normalize_path(image_save_folder)
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
                self.event_queue.put(('wf_info_created', normalized_path, self.target_image_folder, self.wait_time, self.image_save_folder))
                self.log_debug(f"WfInfoFolderHandler: Created event detected for {normalized_path}")

                wf_file_info = extract_file_info(os.path.basename(normalized_path))
                if wf_file_info[0] and wf_file_info[1] and wf_file_info[2]:
                    replace_text_in_files(wf_file_info, self.target_image_folder, self.log_debug, self.log_event)

    def on_modified(self, event):
        if not event.is_directory:
            normalized_path = normalize_path(event.src_path)
            if normalized_path in self.creation_times:
                creation_time = self.creation_times[normalized_path]
                if datetime.now() - creation_time < timedelta(seconds=1):
                    self.log_debug(f"WfInfoFolderHandler: Ignoring modified event for {normalized_path} immediately after creation")
                    return
            event_id = ('modified', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('wf_info_modified', normalized_path, self.target_image_folder, self.wait_time, self.image_save_folder))
                self.log_debug(f"WfInfoFolderHandler: Modified event detected for {normalized_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            normalized_path = normalize_path(event.src_path)
            event_id = ('deleted', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                self.log_event("File Deleted", normalized_path)
                self.log_debug(f"WfInfoFolderHandler: Deleted event detected for {normalized_path}")

    def on_moved(self, event):
        if not event.is_directory:
            normalized_src_path = normalize_path(event.src_path)
            normalized_dest_path = normalize_path(event.dest_path)
            event_id = ('moved', normalized_src_path, normalized_dest_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                self.log_event("File Moved", normalized_src_path, normalized_dest_path)
                self.log_debug(f"WfInfoFolderHandler: Moved event detected from {normalized_src_path} to {normalized_dest_path}")
