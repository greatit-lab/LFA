import configparser
import os
from utils import normalize_path

CONFIG_FILE = 'settings.ini'
EQPID_FILE = 'eqpid.ini'

class CaseSensitiveConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr  # Override to preserve case

def load_eqpid():
    config = configparser.ConfigParser()
    if os.path.exists(EQPID_FILE):
        with open(EQPID_FILE, 'r', encoding='utf-8') as configfile:
            config.read_file(configfile)
            return config.get('General', 'eqpid', fallback='UNKNOWN')
    return None

def save_eqpid(eqpid):
    config = configparser.ConfigParser()
    config['General'] = {'eqpid': eqpid}
    with open(EQPID_FILE, 'w', encoding='utf-8') as configfile:
        config.write(configfile)

def load_settings():
    config = CaseSensitiveConfigParser()
    if not os.path.exists(CONFIG_FILE):
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
            config.read_file(configfile)

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

    monitored_folders = [normalize_path(folder) for key, folder in config.items('Folders')]
    dest_folder = normalize_path(config.get('Destination', 'folder', fallback=''))
    if dest_folder and not os.path.exists(dest_folder):
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

    return monitored_folders, dest_folder, regex_folders, exclude_folders, base_date_folder, target_compare_folders, target_image_folder, wait_time, image_save_folder, wafer_flat_data_path, prealign_data_path, image_data_path

def save_settings(monitored_folders, dest_folder, regex_folders, exclude_folders, base_date_folder, target_compare_folders, target_image_folder, wait_time, image_save_folder, wafer_flat_data_path, prealign_data_path, image_data_path):
    config = CaseSensitiveConfigParser()
    # Filter out base_date_folder and wf_info from monitored_folders before saving
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

    with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
