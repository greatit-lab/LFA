import configparser  # 설정 파일을 읽고 쓰기 위한 모듈을 불러옵니다.
import os  # 운영체제와 상호작용하기 위한 모듈을 불러옵니다.
from utils import normalize_path  # 경로를 정규화하기 위한 유틸리티 함수를 불러옵니다.

# 설정 파일과 EQPID 파일의 이름을 상수로 정의합니다.
CONFIG_FILE = 'settings.ini'
EQPID_FILE = 'eqpid.ini'

# 대소문자를 구분하는 설정 파서를 정의합니다.
class CaseSensitiveConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        # 기본 설정에서는 키의 대소문자를 무시하지만,
        # 이 메소드를 재정의하여 키의 대소문자를 유지하도록 합니다.
        return optionstr

# EQPID(장비 ID)를 설정 파일에서 불러오는 함수입니다.
def load_eqpid():
    config = configparser.ConfigParser()  # ConfigParser 객체를 생성합니다.
    if os.path.exists(EQPID_FILE):  # EQPID 파일이 존재하는지 확인합니다.
        with open(EQPID_FILE, 'r', encoding='utf-8') as configfile:
            config.read_file(configfile)  # EQPID 파일을 읽습니다.
            # 'General' 섹션에서 'eqpid' 키의 값을 가져옵니다.
            return config.get('General', 'eqpid', fallback='UNKNOWN')
    return None  # 파일이 없거나 'eqpid' 값이 없으면 None을 반환합니다.

# EQPID(장비 ID)를 설정 파일에 저장하는 함수입니다.
def save_eqpid(eqpid):
    config = configparser.ConfigParser()  # ConfigParser 객체를 생성합니다.
    config['General'] = {'eqpid': eqpid}  # 'General' 섹션에 'eqpid' 값을 설정합니다.
    with open(EQPID_FILE, 'w', encoding='utf-8') as configfile:
        config.write(configfile)  # EQPID 파일에 저장합니다.

# settings.ini 파일에서 설정을 불러오는 함수입니다.
def load_settings():
    config = CaseSensitiveConfigParser()  # 대소문자를 구분하는 ConfigParser 객체를 생성합니다.
    if not os.path.exists(CONFIG_FILE):  # 설정 파일이 존재하지 않으면,
        # 기본 설정 값을 사용하여 설정 파일을 만듭니다.
        config['Folders'] = {}
        config['Destination'] = {'folder': ''}
        config['Regex'] = {}
        config['Exclude'] = {}
        config['General'] = {'base_date_folder': 'Unselected', 'target_compare_folders': ''}
        config['Image'] = {'target_image_folder': 'Unselected', 'wait_time': '60', 'image_save_folder': ''}
        config['Upload'] = {'wafer_flat_data_path': 'Unselected', 'prealign_data_path': 'Unselected', 'image_data_path': 'Unselected'}
        save_settings([], '', {}, [], 'Unselected', [], 'Unselected', '60', '', 'Unselected', 'Unselected', 'Unselected')
    else:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as configfile:
            config.read_file(configfile)  # 설정 파일을 읽습니다.

        # 설정 파일에 필요한 섹션이 없을 경우, 기본 값을 추가합니다.
        if 'Folders' not in config:
            config['Folders'] = {}
        if 'Destination' not in config:
            config['Destination'] = {'folder': ''}
        if 'Regex' not in config:
            config['Regex'] = {}
        if 'Exclude' not in config:
            config['Exclude'] = {}
        if 'General' not in config:
            config['General'] = {'base_date_folder': 'Unselected', 'target_compare_folders': ''}
        if 'Image' not in config:
            config['Image'] = {'target_image_folder': 'Unselected', 'wait_time': '60', 'image_save_folder': ''}
        if 'Upload' not in config:
            config['Upload'] = {'wafer_flat_data_path': 'Unselected', 'prealign_data_path': 'Unselected', 'image_data_path': 'Unselected'}

    # 설정 파일에서 값을 불러옵니다.
    monitored_folders = [normalize_path(folder) for key, folder in config.items('Folders')]
    dest_folder = normalize_path(config.get('Destination', 'folder', fallback=''))
    if dest_folder and not os.path.exists(dest_folder):  # 폴더가 존재하지 않으면 빈 문자열로 초기화합니다.
        dest_folder = ''
    regex_folders = {regex: normalize_path(folder) for regex, folder in config.items('Regex')}
    exclude_folders = [normalize_path(folder) for key, folder in config.items('Exclude')]
    base_date_folder = config.get('General', 'base_date_folder', fallback='Unselected')
    target_compare_folders = config.get('General', 'target_compare_folders', fallback='').split(';')

    target_image_folder = config.get('Image', 'target_image_folder', fallback='Unselected')
    wait_time = config.get('Image', 'wait_time', fallback='60')
    image_save_folder = config.get('Image', 'image_save_folder', fallback='')

    wafer_flat_data_path = config.get('Upload', 'wafer_flat_data_path', fallback='Unselected')
    prealign_data_path = config.get('Upload', 'prealign_data_path', fallback='Unselected')
    image_data_path = config.get('Upload', 'image_data_path', fallback='Unselected')

    # 불러온 값을 반환합니다.
    return monitored_folders, dest_folder, regex_folders, exclude_folders, base_date_folder, target_compare_folders, target_image_folder, wait_time, image_save_folder, wafer_flat_data_path, prealign_data_path, image_data_path

# settings.ini 파일에 설정을 저장하는 함수입니다.
def save_settings(monitored_folders, dest_folder, regex_folders, exclude_folders, base_date_folder, target_compare_folders, target_image_folder, wait_time, image_save_folder, wafer_flat_data_path, prealign_data_path, image_data_path):
    config = CaseSensitiveConfigParser()  # 대소문자를 구분하는 ConfigParser 객체를 생성합니다.
    # base_date_folder와 wf_info를 필터링하여 저장할 폴더 목록을 만듭니다.
    filtered_folders = [folder for folder in monitored_folders if folder != base_date_folder and not folder.startswith(os.path.join(dest_folder, 'wf_info'))]
    config['Folders'] = {str(i): normalize_path(folder) for i, folder in enumerate(filtered_folders)}
    config['Destination'] = {'folder': normalize_path(dest_folder)}
    config['Regex'] = {regex: normalize_path(folder) for regex, folder in regex_folders.items()}
    config['Exclude'] = {str(i): normalize_path(folder) for i, folder in enumerate(exclude_folders)}
    config['General'] = {
        'base_date_folder': base_date_folder,
        'target_compare_folders': ';'.join(target_compare_folders)
    }
    config['Image'] = {
        'target_image_folder': target_image_folder,
        'wait_time': wait_time,
        'image_save_folder': image_save_folder
    }
    config['Upload'] = {
        'wafer_flat_data_path': wafer_flat_data_path,
        'prealign_data_path': prealign_data_path,
        'image_data_path': image_data_path
    }

    # 설정을 파일에 저장합니다.
    with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
