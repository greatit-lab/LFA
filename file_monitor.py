import os
import re
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timedelta
from performance_monitor import PerformanceMonitor
import queue
import threading
from utils import normalize_path
from logger import log_event, log_debug
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from concurrent.futures import ThreadPoolExecutor, as_completed

def images_to_pdf(image_paths, output_folder, base_name):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_path = os.path.join(output_folder, f"{base_name}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)

    for image_path in image_paths:
        img = Image.open(image_path)
        img_width, img_height = img.size

        # 페이지 크기를 이미지 크기로 설정
        c.setPageSize((img_width, img_height))

        # 이미지를 PDF에 추가
        c.drawImage(image_path, 0, 0, img_width, img_height)
        c.showPage()

    c.save()

def extract_file_info(filename):
    # Extract datetime, compare string, and extract string from filename
    match = re.match(r"(\d{8}_\d{6})_([A-Z0-9.]+)_([A-Z0-9]+)_", filename)
    if match:
        datetime_str, compare_str, extract_str = match.groups()
        return datetime_str, compare_str, extract_str
    return None, None, None

def replace_text_in_files(wf_file_info, target_folder, log_debug, log_event):
    # Replace #1 in filenames with the extract string if datetime and compare string match
    wf_datetime, wf_compare, wf_extract = wf_file_info
    log_debug(f"Attempting to replace text in files in {target_folder} matching {wf_file_info}")
    for root, _, files in os.walk(target_folder):
        for filename in files:
            if wf_datetime in filename and wf_compare in filename:
                old_path = os.path.join(root, filename)
                new_filename = filename.replace("#1", wf_extract)
                new_path = os.path.join(root, new_filename)
                if "#1" in filename:
                    log_debug(f"Renaming {old_path} to {new_path}")
                    os.rename(old_path, new_path)
                    log_event("File Renamed", f"{old_path} -> {new_filename}")

def create_file_based_on_datetime(file_path, log_debug, log_event, save_to_folder):
    try:
        log_debug(f"Reading file for datetime extraction: {file_path}")
        with open(file_path, 'r', encoding='cp949') as file:
            content = file.read()
        
        match = re.search(r"Date and Time:\s+(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\s+[APM]{2})", content)
        if match:
            log_debug(f"Match found: {match.group(1)}")
            datetime_str = datetime.strptime(match.group(1), '%m/%d/%Y %I:%M:%S %p').strftime('%Y%m%d_%H%M%S')
            _, file_name = os.path.split(file_path)
            
            # Ensure 'wf_info' directory exists
            wf_info_dir = os.path.join(save_to_folder, 'wf_info')
            if not os.path.exists(wf_info_dir):
                os.makedirs(wf_info_dir)
                log_debug(f"Created directory {wf_info_dir}")

            new_file_name = f"{datetime_str}_{file_name.rsplit('.', 1)[0]}.na"
            new_file_path = os.path.join(wf_info_dir, new_file_name)
            
            # Create an empty file
            with open(new_file_path, 'w', encoding='cp949') as new_file:
                new_file.write("")  # Write an empty string to create an empty file
            
            log_debug(f"Created empty file {new_file_path} based on {file_path}")
            log_event("File Created", new_file_path)
            return True
        else:
            log_debug(f"No Date and Time found in {file_path}")
            return False
    except Exception as e:
        log_debug(f"Error creating file based on {file_path}: {str(e)}")
        return False

class BaseDateFolderHandler(FileSystemEventHandler):
    def __init__(self, base_date_folder, save_to_folder, log_event, log_debug, event_queue, processed_events, target_image_folder, wait_time, image_save_folder):
        self.base_date_folder = normalize_path(base_date_folder)
        self.save_to_folder = normalize_path(save_to_folder)
        self.log_event = log_event
        self.log_debug = log_debug
        self.event_queue = event_queue
        self.processed_events = processed_events
        self.creation_times = {}
        self.target_image_folder = normalize_path(target_image_folder)
        self.wait_time = int(wait_time)
        self.image_save_folder = normalize_path(image_save_folder)

    def on_created(self, event):
        if not event.is_directory:
            normalized_path = normalize_path(event.src_path)
            self.creation_times[normalized_path] = datetime.now()
            event_id = ('created', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('base_date_created', normalized_path, self.target_image_folder, self.wait_time, self.image_save_folder))
                self.log_debug(f"Created event detected for {normalized_path}")

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
                self.event_queue.put(('base_date_modified', normalized_path, self.target_image_folder, self.wait_time, self.image_save_folder))
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

class TargetFoldersHandler(FileSystemEventHandler):
    def __init__(self, dest_folder, regex_folders, exclude_folders, log_event, log_debug, event_queue, processed_events):
        self.dest_folder = normalize_path(dest_folder)
        self.regex_folders = {pattern: normalize_path(folder) for pattern, folder in regex_folders.items()}
        self.exclude_folders = [normalize_path(folder) for folder in exclude_folders]
        self.log_event = log_event
        self.log_debug = log_debug
        self.event_queue = event_queue
        self.processed_events = processed_events
        self.creation_times = {}

    def is_excluded(self, path):
        normalized_path = normalize_path(path)
        return any(normalized_path.startswith(exclude_folder) for exclude_folder in self.exclude_folders)

    def on_created(self, event):
        if not event.is_directory and not self.is_excluded(event.src_path):
            normalized_path = normalize_path(event.src_path)
            self.creation_times[normalized_path] = datetime.now()
            event_id = ('created', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('created', normalized_path))
                self.log_debug(f"Created event detected for {normalized_path}")

    def on_modified(self, event):
        if not event.is_directory and not self.is_excluded(event.src_path):
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
        if not event.is_directory and not self.is_excluded(event.src_path):
            normalized_path = normalize_path(event.src_path)
            event_id = ('deleted', normalized_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('deleted', normalized_path))
                self.log_debug(f"Deleted event detected for {normalized_path}")

    def on_moved(self, event):
        if not event.is_directory and not self.is_excluded(event.src_path):
            normalized_src_path = normalize_path(event.src_path)
            normalized_dest_path = normalize_path(event.dest_path)
            event_id = ('moved', normalized_src_path, normalized_dest_path)
            if event_id not in self.processed_events or datetime.now() - self.processed_events[event_id] > timedelta(seconds=1):
                self.processed_events[event_id] = datetime.now()
                self.event_queue.put(('moved', normalized_src_path, normalized_dest_path))
                self.log_debug(f"Moved event detected from {normalized_src_path} to {normalized_dest_path}")

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

                # Process new file in wf_info folder
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

def process_images(event_type, src_path, target_image_folder, wait_time, save_to_folder):
    log_debug(f"Processing images for {event_type} event: {src_path}")

    # Extract datetime and specific pattern from the filename
    filename = os.path.basename(src_path)
    datetime_str, specific_pattern = filename.split('_')[:2]

    # Wait for the specified wait time
    log_debug(f"Waiting for {wait_time} seconds before processing images.")
    time.sleep(wait_time)

    # Find matching image files in the target image folder
    matching_images = []
    for root, _, files in os.walk(target_image_folder):
        for file in files:
            if datetime_str in file and specific_pattern in file:
                matching_images.append(os.path.join(root, file))

    # Convert matching images to PDF
    if matching_images:
        log_debug(f"Found {len(matching_images)} matching images. Converting to PDF.")
        images_to_pdf(matching_images, save_to_folder, f"{datetime_str}_{specific_pattern}")
    else:
        log_debug("No matching images found.")

def event_processor(event_queue, log_event, log_debug, perf_monitor, dest_folder, regex_folders, base_date_folder, save_to_folder, target_compare_folders):
    executor = ThreadPoolExecutor(max_workers=4)
    futures = []

    while True:
        try:
            event = event_queue.get(timeout=1)
            log_debug(f"Processing event: {event}")
        except queue.Empty:
            continue
        try:
            event_type, src_path, *extra = event
            target_image_folder = extra[0] if extra else None
            wait_time = extra[1] if extra else None
            image_save_folder = extra[2] if extra else None

            if event_type in ['created', 'modified', 'deleted', 'moved']:
                perf_monitor.log_performance()

            if event_type in ['created', 'modified']:
                matched = False
                for pattern, subfolder in regex_folders.items():
                    if re.search(pattern, os.path.basename(src_path)):
                        dest_path = normalize_path(os.path.join(dest_folder, subfolder, os.path.basename(src_path)))
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        if normalize_path(src_path) != normalize_path(dest_path):
                            try:
                                shutil.copy2(src_path, dest_path)
                                log_event(event_type, src_path, dest_path)
                                log_debug(f"File {event_type} and copied to {dest_path}")
                            except Exception as e:
                                log_debug(f"Error copying file {src_path} to {dest_path}: {str(e)}")
                        else:
                            log_debug(f"Source and destination are the same: {src_path}")
                        matched = True
                        break
                if not matched:
                    log_event(event_type, src_path)
                    log_debug(f"File {event_type} but no matching regex pattern found for copying")

            elif event_type == 'deleted':
                log_event("deleted", src_path)
                log_debug(f"Processing event: deleted for {src_path}")
            elif event_type == 'moved':
                log_event("moved", src_path, dest_path)

            elif event_type in ['base_date_created', 'base_date_modified']:
                create_file_based_on_datetime(src_path, log_debug, log_event, save_to_folder)
                if target_image_folder and wait_time and image_save_folder:
                    future = executor.submit(process_images, event_type, src_path, target_image_folder, wait_time, image_save_folder)
                    futures.append(future)

        except Exception as e:
            log_debug(f"Error processing event {event}: {str(e)}")

    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            log_debug(f"Error in processing images: {str(e)}")

def start_monitoring(app):
    log_dir = app.logger.log_dir_path
    perf_monitor = PerformanceMonitor(log_dir)
    event_queue = queue.Queue()
    processed_events = {}  # Dictionary to store processed event identifiers and their timestamps
    exclude_folders = app.app_context.exclude_folders  # Assuming exclude_folders is defined in app_context
    save_to_folder = app.app_context.dest_folder  # Save to Folder 지정된 폴더 경로
    target_image_folder = app.image_trans_frame.target_image_folder_combo.currentText()
    wait_time = app.image_trans_frame.wait_time_combo.currentText()
    image_save_folder = app.image_trans_frame.image_save_folder_path.text()  # 수정된 부분

    # If base_date_folder is "Unselected", do not monitor it
    base_date_folder = app.app_context.base_date_folder
    monitored_paths = app.app_context.monitored_folders
    if base_date_folder != "Unselected":
        monitored_paths += [base_date_folder]  # Add base_date_folder to monitored paths

    # Initialize handlers for Base Date Folder, Target Folders, and wf_info folder separately
    base_date_folder_handler = BaseDateFolderHandler(
        base_date_folder,
        save_to_folder,
        app.logger.log_event,
        app.logger.log_debug,
        event_queue,
        processed_events,
        target_image_folder,
        wait_time,
        image_save_folder
    )

    target_folders_handler = TargetFoldersHandler(
        app.app_context.dest_folder,
        app.app_context.regex_folders,
        exclude_folders,
        app.logger.log_event,
        app.logger.log_debug,
        event_queue,
        processed_events
    )

    wf_info_folder_handler = WfInfoFolderHandler(
        app.app_context.target_compare_folders,
        app.logger.log_event,
        app.logger.log_debug,
        event_queue,
        processed_events
    )

    observer = Observer()
    # Schedule base date folder handler
    if base_date_folder != "Unselected":
        observer.schedule(base_date_folder_handler, path=base_date_folder, recursive=True)
    # Schedule target folders handler
    for path in monitored_paths:
        observer.schedule(target_folders_handler, path=path, recursive=True)
    # Schedule wf_info folder handler
    observer.schedule(wf_info_folder_handler, path=os.path.join(save_to_folder, 'wf_info'), recursive=True)
    
    observer.start()
    if not hasattr(app, 'monitoring_started') or not app.monitoring_started:
        app.logger.log_event("Monitoring started", "")
        app.monitoring_started = True

    processor_thread = threading.Thread(target=event_processor, args=(event_queue, app.logger.log_event, app.logger.log_debug, perf_monitor, app.app_context.dest_folder, app.app_context.regex_folders, base_date_folder, save_to_folder, app.app_context.target_compare_folders))
    processor_thread.daemon = True
    processor_thread.start()
    app.logger.log_debug("Processor thread started")

    try:
        while not app.stop_event.is_set():
            app.stop_event.wait(1)
    finally:
        observer.stop()
        observer.join()
        if app.monitoring_started:
            app.logger.log_event("Monitoring stopped", "")
            app.monitoring_started = False
        app.logger.log_debug("Observer stopped")