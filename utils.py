import os

def normalize_path(path):
    return path.replace('\\', '/')

def get_log_file_size(file_path):
    return os.path.getsize(file_path) if os.path.exists(file_path) else 0
