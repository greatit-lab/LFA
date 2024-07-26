import os
import queue
import threading
from watchdog.observers import Observer
from performance_monitor import PerformanceMonitor
from utils import normalize_path
from file_monitor.base_date_folder_handler import BaseDateFolderHandler
from file_monitor.target_folders_handler import TargetFoldersHandler
from file_monitor.wf_info_folder_handler import WfInfoFolderHandler
from file_monitor.event_processor import event_processor

def start_monitoring(app):
    log_dir = app.logger.log_dir_path
    perf_monitor = PerformanceMonitor(log_dir)
    event_queue = queue.Queue()
    processed_events = {}
    exclude_folders = app.app_context.exclude_folders
    save_to_folder = app.app_context.dest_folder
    target_image_folder = app.image_trans_frame.target_image_folder_combo.currentText()
    wait_time = app.image_trans_frame.wait_time_combo.currentText()
    image_save_folder = app.image_trans_frame.image_save_folder_path.text()

    base_date_folder = app.app_context.base_date_folder
    monitored_paths = app.app_context.monitored_folders
    if base_date_folder != "Unselected":
        monitored_paths += [base_date_folder]

    base_date_folder_handler = BaseDateFolderHandler(
        base_date_folder,
        save_to_folder,
        app.logger.log_event,
        app.logger.log_debug,
        event_queue,
        processed_events
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
        target_image_folder,
        wait_time,
        image_save_folder,
        app.logger.log_event,
        app.logger.log_debug,
        event_queue,
        processed_events
    )

    observer = Observer()
    if base_date_folder != "Unselected":
        observer.schedule(base_date_folder_handler, path=base_date_folder, recursive=True)
        app.logger.log_debug(f"Monitoring started for base_date_folder: {base_date_folder}")
    for path in monitored_paths:
        observer.schedule(target_folders_handler, path=path, recursive=True)
        app.logger.log_debug(f"Monitoring started for path: {path}")
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
