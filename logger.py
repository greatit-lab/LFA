import logging
import os
from datetime import datetime

# 로그 파일을 설정하는 함수
def setup_event_logging(log_dir):
    # 오늘 날짜를 'YYYYMMDD' 형식으로 가져옵니다.
    date_str = datetime.now().strftime('%Y%m%d')
    # 이벤트 로그 파일의 경로를 설정합니다. 예: 'log_dir/20230731_event.log'
    event_log_file_path = os.path.join(log_dir, f"{date_str}_event.log")

    # 'event_logger'라는 이름의 로거(logger)를 만듭니다.
    event_logger = logging.getLogger('event_logger')
    # 로그 레벨을 INFO로 설정합니다. (정보 수준의 로그를 기록합니다.)
    event_logger.setLevel(logging.INFO)

    # 파일 핸들러(file handler)를 만들어 로그를 파일에 기록하게 합니다.
    event_handler = logging.FileHandler(event_log_file_path, 'a', 'utf-8')
    # 로그 메시지의 형식을 설정합니다. (로그에 시간과 메시지를 포함합니다.)
    event_formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    event_handler.setFormatter(event_formatter)

    # 이미 다른 핸들러가 설정되어 있지 않은 경우, 새로 만든 핸들러를 추가합니다.
    if not event_logger.hasHandlers():
        event_logger.addHandler(event_handler)

# 디버그 로그를 설정하는 함수
def add_debug_logging(log_dir):
    # 오늘 날짜를 'YYYYMMDD' 형식으로 가져옵니다.
    date_str = datetime.now().strftime('%Y%m%d')
    # 디버그 로그 파일의 경로를 설정합니다. 예: 'log_dir/20230731_debug.log'
    debug_log_file_path = os.path.join(log_dir, f"{date_str}_debug.log")

    # 파일 핸들러(file handler)를 만들어 로그를 파일에 기록하게 합니다.
    debug_handler = logging.FileHandler(debug_log_file_path, 'a', 'utf-8')
    # 로그 레벨을 DEBUG로 설정합니다. (디버그 수준의 로그를 기록합니다.)
    debug_handler.setLevel(logging.DEBUG)
    # 로그 메시지의 형식을 설정합니다. (로그에 시간과 메시지를 포함합니다.)
    debug_formatter = logging.Formatter('%(asctime)s.%(msecs)03d - DEBUG: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    debug_handler.setFormatter(debug_formatter)

    # 'debug_logger'라는 이름의 로거(logger)를 만듭니다.
    logger = logging.getLogger('debug_logger')
    # 로그 레벨을 DEBUG로 설정합니다.
    logger.setLevel(logging.DEBUG)
    # 이미 다른 핸들러가 설정되어 있지 않은 경우, 새로 만든 핸들러를 추가합니다.
    if not logger.hasHandlers():
        logger.addHandler(debug_handler)
    
    # 디버그 메시지를 기록합니다.
    logger.debug(f"Debug logging added with file: {debug_log_file_path}")

# 디버그 로그 핸들러를 제거하는 함수
def remove_debug_logging():
    # 'debug_logger'라는 이름의 로거(logger)를 가져옵니다.
    logger = logging.getLogger('debug_logger')
    # 디버그 로그 핸들러만 제거하고 다른 핸들러는 유지합니다.
    handlers_to_keep = [h for h in logger.handlers if not (isinstance(h, logging.FileHandler) and h.level == logging.DEBUG)]
    logger.handlers = handlers_to_keep

# 파일 이벤트(생성, 수정, 삭제 등)를 기록하는 함수
def log_event(event_type, src_path=None, dest_path=None):
    # 'event_logger'라는 이름의 로거(logger)를 가져옵니다.
    event_logger = logging.getLogger('event_logger')
    # 이벤트 유형에 따라 로그 메시지를 기록합니다.
    if event_type in ["Monitoring started", "Monitoring stopped", "Application quit"]:
        event_logger.info(f"File {event_type}:")
    elif event_type in ["created", "modified"]:
        event_logger.info(f"File {event_type}: {src_path} -> copied to: {dest_path if dest_path else 'unknown destination'}")
    else:
        event_logger.info(f"File {event_type}: {src_path} {'-> ' + dest_path if dest_path else ''}")

# 디버그 메시지를 기록하는 함수
def log_debug(message):
    # 'debug_logger'라는 이름의 로거(logger)를 가져옵니다.
    debug_logger = logging.getLogger('debug_logger')
    # 디버그 메시지를 기록합니다.
    debug_logger.debug(message)

# 특정 이벤트에 대한 디버그 로그를 기록하는 함수
def log_debug_event(event_type, src_path=None, dest_path=None, additional_message=None):
    # 'debug_logger'라는 이름의 로거(logger)를 가져옵니다.
    debug_logger = logging.getLogger('debug_logger')
    # 추가 메시지가 있으면 그 메시지를 기록합니다.
    if additional_message:
        debug_logger.debug(additional_message)
    # 이벤트 유형에 따라 로그 메시지를 기록합니다.
    elif event_type in ["created", "modified", "deleted", "moved"]:
        if event_type in ["created", "modified"]:
            debug_logger.debug(f"File {event_type} and copied to {dest_path}")
        debug_logger.debug(f"{event_type.capitalize()} event detected for {src_path}")
        debug_logger.debug(f"Processing event: {event_type} for {src_path}")
    else:
        debug_logger.debug(event_type)

# 기본 로깅 설정을 업데이트하는 함수
def update_logging_config(log_file_path):
    # 로깅 설정을 기본값으로 설정합니다. (로그를 파일에 기록하고, 시간, 로그 레벨, 메시지를 포함합니다.)
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
