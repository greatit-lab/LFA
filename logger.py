import logging
import os
from datetime import datetime

def setup_event_logging(log_dir):
    date_str = datetime.now().strftime('%Y%m%d')
    event_log_file_path = os.path.join(log_dir, f"{date_str}_event.log")

    event_logger = logging.getLogger('event_logger')
    event_logger.setLevel(logging.INFO)

    event_handler = logging.FileHandler(event_log_file_path, 'a', 'utf-8')
    event_formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    event_handler.setFormatter(event_formatter)

    if not event_logger.hasHandlers():
        event_logger.addHandler(event_handler)

def add_debug_logging(log_dir):
    date_str = datetime.now().strftime('%Y%m%d')
    debug_log_file_path = os.path.join(log_dir, f"{date_str}_debug.log")

    debug_handler = logging.FileHandler(debug_log_file_path, 'a', 'utf-8')
    debug_handler.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter('%(asctime)s.%(msecs)03d - DEBUG: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    debug_handler.setFormatter(debug_formatter)

    logger = logging.getLogger('debug_logger')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(debug_handler)
    logger.debug(f"Debug logging added with file: {debug_log_file_path}")

def remove_debug_logging():
    logger = logging.getLogger('debug_logger')
    handlers_to_keep = [h for h in logger.handlers if not (isinstance(h, logging.FileHandler) and h.level == logging.DEBUG)]
    logger.handlers = handlers_to_keep

def log_event(event_type, src_path=None, dest_path=None):
    event_logger = logging.getLogger('event_logger')
    if event_type in ["Monitoring started", "Monitoring stopped", "Application quit"]:
        event_logger.info(f"File {event_type}:")
    elif event_type in ["created", "modified"]:
        event_logger.info(f"File {event_type}: {src_path} -> copied to: {dest_path if dest_path else 'unknown destination'}")
    else:
        event_logger.info(f"File {event_type}: {src_path} {'-> ' + dest_path if dest_path else ''}")

def log_debug(message):
    debug_logger = logging.getLogger('debug_logger')
    debug_logger.debug(message)

def log_debug_event(event_type, src_path=None, dest_path=None, additional_message=None):
    debug_logger = logging.getLogger('debug_logger')
    if additional_message:
        debug_logger.debug(additional_message)
    elif event_type in ["created", "modified", "deleted", "moved"]:
        if event_type in ["created", "modified"]:
            debug_logger.debug(f"File {event_type} and copied to {dest_path}")
        debug_logger.debug(f"{event_type.capitalize()} event detected for {src_path}")
        debug_logger.debug(f"Processing event: {event_type} for {src_path}")
    else:
        debug_logger.debug(event_type)

def update_logging_config(log_file_path):
    logging.basicConfig(
        filename=log_file_path,
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
