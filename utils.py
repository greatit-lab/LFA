import os  # 운영체제와 상호작용하기 위한 모듈을 불러옵니다.

# 경로를 정규화하여 반환하는 함수입니다.
def normalize_path(path):
    """
    주어진 경로를 현재 운영체제에 맞는 표준 경로 형식으로 변환합니다.
    예를 들어, Windows에서는 경로의 슬래시('/')를 역슬래시('\\')로 바꾸는 등의 작업을 수행합니다.
    
    Args:
        path (str): 변환할 경로 문자열.
    
    Returns:
        str: 정규화된 경로 문자열.
    """
    return os.path.normpath(path)

# 로그 파일의 크기를 반환하는 함수입니다.
def get_log_file_size(file_path):
    """
    주어진 파일의 크기를 바이트 단위로 반환합니다.
    파일의 크기를 확인할 때 사용됩니다.
    
    Args:
        file_path (str): 파일의 경로.
    
    Returns:
        int: 파일의 크기(바이트 단위).
    """
    try:
        return os.path.getsize(file_path)  # 파일의 크기를 바이트 단위로 반환합니다.
    except OSError:
        return 0  # 파일이 존재하지 않거나 접근할 수 없을 때 0을 반환합니다.
