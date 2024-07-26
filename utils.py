import os

def normalize_path(path):
    """Normarliz the path to use the correct separator for the current operating system"""
    return os.path.normpath(path)

def get_log_file_size(file_path):
    try:
        return os.path.getsize(file_path)
    except OSError:
        retrun 0