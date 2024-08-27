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
    # 로그 파일이 저장될 디렉토리를 가져옵니다.
    log_dir = app.logger.log_dir_path

    # 성능 모니터링 객체를 초기화합니다. (로그 디렉토리를 사용합니다.)
    perf_monitor = PerformanceMonitor(log_dir)

    # 이벤트를 저장할 큐(queue)를 생성합니다.
    event_queue = queue.Queue()

    # 이미 처리된 이벤트를 추적하기 위한 딕셔너리를 초기화합니다.
    processed_events = {}

    # 설정된 제외 폴더와 저장 폴더를 가져옵니다.
    exclude_folders = app.app_context.exclude_folders
    save_to_folder = app.app_context.dest_folder

    # 이미지 변환에 필요한 설정들을 가져옵니다.
    target_image_folder = app.image_trans_frame.target_image_folder_combo.currentText()
    wait_time = app.image_trans_frame.wait_time_combo.currentText()
    image_save_folder = app.image_trans_frame.image_save_folder_path.text()

    # 기본 날짜 폴더와 모니터링할 폴더들을 가져옵니다.
    base_date_folder = app.app_context.base_date_folder
    monitored_paths = app.app_context.monitored_folders
    if base_date_folder != "Unselected":  # 기본 날짜 폴더가 선택된 경우
        monitored_paths += [base_date_folder]

    # 기본 날짜 폴더 핸들러를 초기화합니다.
    base_date_folder_handler = BaseDateFolderHandler(
        base_date_folder,
        save_to_folder,
        app.logger.log_event,
        app.logger.log_debug,
        event_queue,
        processed_events
    )

    # 타겟 폴더 핸들러를 초기화합니다.
    target_folders_handler = TargetFoldersHandler(
        app.app_context.dest_folder,
        app.app_context.regex_folders,
        exclude_folders,
        app.logger.log_event,
        app.logger.log_debug,
        event_queue,
        processed_events
    )

    # WF 정보 폴더 핸들러를 초기화합니다.
    wf_info_folder_handler = WfInfoFolderHandler(
        target_image_folder,
        wait_time,
        image_save_folder,
        app.logger.log_event,
        app.logger.log_debug,
        event_queue,
        processed_events
    )

    # 파일 시스템 변경 사항을 감시하는 Observer 객체를 초기화합니다.
    observer = Observer()
    
    # 기본 날짜 폴더가 선택된 경우 해당 폴더를 모니터링하도록 설정합니다.
    if base_date_folder != "Unselected":
        observer.schedule(base_date_folder_handler, path=base_date_folder, recursive=True)
        app.logger.log_debug(f"Monitoring started for base_date_folder: {base_date_folder}")
    
    # 모니터링할 모든 경로에 대해 이벤트 핸들러를 설정합니다.
    for path in monitored_paths:
        observer.schedule(target_folders_handler, path=path, recursive=True)
        app.logger.log_debug(f"start_monitoring: Monitoring started for path: {path}")
    
    # wf_info 폴더도 모니터링하도록 설정합니다.
    observer.schedule(wf_info_folder_handler, path=os.path.join(save_to_folder, 'wf_info'), recursive=True)
    
    # 파일 시스템 변경 감시를 시작합니다.
    observer.start()

    # 애플리케이션의 모니터링 상태를 설정합니다.
    if not hasattr(app, 'monitoring_started') or not app.monitoring_started:
        app.logger.log_event("Monitoring started", "")
        app.monitoring_started = True

    # 이벤트를 처리하는 스레드를 시작합니다.
    processor_thread = threading.Thread(
        target=event_processor, 
        args=(
            event_queue, 
            app.logger.log_event, 
            app.logger.log_debug, 
            perf_monitor, 
            app.app_context.dest_folder, 
            app.app_context.regex_folders, 
            base_date_folder, 
            save_to_folder, 
            app.app_context.target_compare_folders
        )
    )
    processor_thread.daemon = True
    processor_thread.start()
    app.logger.log_debug("start_monitoring: Processor thread started")

    try:
        # 메인 스레드는 stop_event가 설정될 때까지 대기합니다.
        while not app.stop_event.is_set():
            app.stop_event.wait(1)
    finally:
        # 모니터링 중지 시, 감시를 중지하고 자원을 정리합니다.
        observer.stop()
        observer.join()
        if app.monitoring_started:
            app.logger.log_event("Monitoring stopped", "")
            app.monitoring_started = False
        app.logger.log_debug("start_monitoring: Observer stopped")
