import os
import re
import shutil
import time
import queue
from datetime import datetime
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from utils import normalize_path

# 파일 이름에서 특정 정보를 추출하는 함수입니다.
# 예를 들어 '20230825_123456_A12345_B67890_' 같은 이름에서 날짜, 비교 문자열, 추출 문자열을 추출합니다.
# 이를 통해 나중에 파일을 식별하거나 다른 작업에 사용할 수 있습니다.
def extract_file_info(filename):
    # 정규 표현식을 사용하여 날짜와 특정 패턴을 추출합니다.
    match = re.match(r"(\d{8}_\d{6})_([A-Z0-9.]+)_([A-Z0-9]+)_", filename)
    if match:
        # 날짜, 비교 문자열, 추출 문자열을 반환합니다.
        datetime_str, compare_str, extract_str = match.groups()
        return datetime_str, compare_str, extract_str
    # 매칭이 되지 않으면 None을 반환합니다.
    return None, None, None

# 지정된 폴더 내에서 파일 이름의 특정 텍스트를 바꾸는 함수입니다.
# 예를 들어, 파일 이름에 포함된 "#1"을 다른 문자열로 바꿉니다.
def replace_text_in_files(wf_file_info, target_folder, log_debug, log_event):
    # 파일에서 추출한 정보를 사용하여 파일을 찾고 이름을 변경합니다.
    wf_datetime, wf_compare, wf_extract = wf_file_info
    log_debug(f"event_processor: Attempting to replace text in files in {target_folder} matching {wf_file_info}")
    for root, _, files in os.walk(target_folder):
        for filename in files:
            # 파일 이름에 특정 문자열이 포함되어 있는지 확인합니다.
            if wf_datetime in filename and wf_compare in filename:
                old_path = os.path.join(root, filename)
                new_filename = filename.replace("#1", wf_extract)
                new_path = os.path.join(root, new_filename)
                if "#1" in filename:
                    log_debug(f"event_processor: Renaming {old_path} to {new_path}")
                    # 파일 이름을 새 이름으로 변경합니다.
                    os.rename(old_path, new_path)
                    log_event("File Renamed", f"{old_path} -> {new_filename}")

# 여러 파일 경로에서 공통된 이름 부분을 추출하는 함수입니다.
# 예를 들어, 'file_01.txt', 'file_02.txt'에서 'file_'을 추출합니다.
def extract_common_name(file_paths):
    if not file_paths:
        return ""
    
    base_name = os.path.basename(file_paths[0])
    # 파일 이름에서 공통된 접두사를 찾습니다.
    match = re.match(r"(.+)_\d+\.\w+$", base_name)
    if not match:
        return base_name
    
    common_name = match.group(1)
    
    for path in file_paths[1:]:
        base_name = os.path.basename(path)
        match = re.match(r"(.+)_\d+\.\w+$", base_name)
        if not match or not base_name.startswith(common_name):
            return os.path.commonprefix([common_name, base_name])
    
    return common_name

# 파일 내용을 읽고 특정 날짜와 시간 정보를 추출하여 새로운 파일을 생성하는 함수입니다.
def create_file_based_on_datetime(file_path, log_debug, log_event, save_to_folder):
    # 여러 인코딩 방식을 시도하여 파일을 읽습니다.
    encodings = ['cp949', 'utf-8', 'latin1']     # 시도할 인코딩 목록
    content = None
    
    for encoding in encodings:
        try:
            log_debug(f"event_processor: Trying to read file with {encoding} encoding: {file_path}")
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
                log_debug(f"event_processor: File content read successfully with {encoding} encoding.")
                break   # 성공하면 반복을 중단
        except Exception as e:
            log_debug(f"event_processor: Error reading file with {encoding} encoding: {str(e)}")
    
    if content is None:
        log_debug(f"event_processor: Failed to read file with all attempted encodings: {file_path}")
        return False
    
    # 파일 내용에서 'Date and Time' 정보를 추출합니다.
    match = re.search(r"Date and Time:\s+(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\s+[APM]{2})", content)
    if match:
        log_debug(f"event_processor: Match found: {match.group(1)}")
        datetime_str = datetime.strptime(match.group(1), '%m/%d/%Y %I:%M:%S %p').strftime('%Y%m%d_%H%M%S')
        _, file_name = os.path.split(file_path)
        
        # 파일을 저장할 디렉토리를 생성합니다.
        wf_info_dir = os.path.join(save_to_folder, 'wf_info')
        if not os.path.exists(wf_info_dir):
            os.makedirs(wf_info_dir)
            log_debug(f"event_processor: Created directory {wf_info_dir}")

        # 새 파일 이름을 생성하고 빈 파일을 만듭니다.
        new_file_name = f"{datetime_str}_{file_name.rsplit('.', 1)[0]}.na"
        new_file_path = os.path.join(wf_info_dir, new_file_name)
        
        with open(new_file_path, 'w', encoding='cp949') as new_file:
            new_file.write("")
        
        log_debug(f"event_processor: Created empty file {new_file_path} based on {file_path}")
        log_event("File Created", new_file_path)
        return True
    else:
        log_debug(f"event_processor: No Date and Time found in {file_path}")
        return False

# 이미지 파일들을 PDF로 변환하는 함수입니다.
def images_to_pdf(image_paths, output_folder, base_name):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_path = os.path.join(output_folder, f"{base_name}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)

    for image_path in image_paths:
        img = Image.open(image_path)
        img_width, img_height = img.size

        # 페이지 크기를 이미지 크기로 설정합니다.
        c.setPageSize((img_width, img_height))

        # 이미지를 PDF에 추가합니다.
        c.drawImage(image_path, 0, 0, img_width, img_height)
        c.showPage()

    c.save()

# 이미지 이벤트를 처리하고, 필요 시 이미지들을 PDF로 변환하는 함수입니다.
def process_images(event_type, src_path, target_image_folder, wait_time, image_save_folder, log_debug):
    log_debug(f"event_processor: Processing images for {event_type} event: {src_path}")

    filename = os.path.basename(src_path)
    datetime_str, specific_pattern = filename.split('_')[:2]

    log_debug(f"event_processor: Waiting for {wait_time} seconds before processing images.")
    time.sleep(wait_time)

    matching_images = []
    for root, _, files in os.walk(target_image_folder):
        for file in files:
            if specific_pattern in file and datetime_str in file:
                matching_images.append(os.path.join(root, file))

    if matching_images:
        log_debug(f"event_processor: Found {len(matching_images)} matching images. Converting to PDF.")
        base_name = extract_common_name(matching_images)
        images_to_pdf(matching_images, image_save_folder, base_name)
    else:
        log_debug("event_processor: No matching images found.")

# 이벤트 큐에서 이벤트를 가져와 처리하는 메인 루프입니다.
def event_processor(event_queue, log_event, log_debug, perf_monitor, dest_folder, regex_folders, base_date_folder, save_to_folder, target_compare_folders):
    while True:
        try:
            # 큐에서 이벤트를 가져옵니다. 이 이벤트는 파일 생성, 수정, 삭제 또는 이동과 같은 파일 시스템에서 발생한 이벤트를 나타냅니다.
            event = event_queue.get(timeout=1)  # 큐에서 이벤트를 기다립니다.
            log_debug(f"event_processor: Received event: {event}")
        except queue.Empty:
            continue  # 이벤트가 없으면 루프를 계속 돌면서 기다립니다.
        
        try:
            event_type, src_path, *extra = event
            target_image_folder = extra[0] if len(extra) > 0 else None
            wait_time = extra[1] if len(extra) > 1 else None
            image_save_folder = extra[2] if len(extra) > 2 else save_to_folder
            
            log_debug(f"event_processor: Processing event of type '{event_type}' for file: {src_path}")

            # 이벤트 유형에 따라 다른 작업을 수행합니다.
            if event_type in ['created', 'modified', 'deleted', 'moved']:
                # 이벤트가 발생하면 성능 로그를 기록합니다.
                perf_monitor.log_performance()

            if event_type in ['created', 'modified']:
                # 파일이 생성되거나 수정되었을 때 처리하는 로직입니다.
                matched = False
                for pattern, subfolder in regex_folders.items():
                    if re.search(pattern, os.path.basename(src_path)):
                        # 파일을 지정된 경로로 복사합니다.
                        dest_path = normalize_path(os.path.join(dest_folder, subfolder, os.path.basename(src_path)))
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        if normalize_path(src_path) != normalize_path(dest_path):
                            try:
                                shutil.copy2(src_path, dest_path)
                                log_event(event_type, src_path, dest_path)
                                log_debug(f"File {event_type} detected. Copied to {dest_path}")
                            except Exception as e:
                                log_debug(f"event_processor: Error copying file {src_path} to {dest_path}: {str(e)}")
                        else:
                            log_debug(f"event_processor: Source and destination paths are the same: {src_path}")
                        matched = True
                        break
                if not matched:
                    log_event(event_type, src_path)
                    log_debug(f"event_processor: File {event_type} detected but no matching regex pattern found for copying.")

            elif event_type == 'deleted':
                # 파일이 삭제되었을 때 처리하는 로직입니다.
                log_event("deleted", src_path)
                log_debug(f"event_processor: Processed 'deleted' event for file: {src_path}")
            elif event_type == 'moved':
                # 파일이 이동되었을 때 처리하는 로직입니다.
                dest_path = extra[0] if extra else None
                log_event("moved", src_path, dest_path)
                log_debug(f"event_processor: Processed 'moved' event from {src_path} to {dest_path}")

            elif event_type in ['base_date_created', 'base_date_modified']:
                # 기본 날짜 폴더가 생성되거나 수정되었을 때 처리하는 로직입니다.
                log_debug(f"event_processor: Processing base date event: {event_type} for file: {src_path}")
                success = create_file_based_on_datetime(src_path, log_debug, log_event, save_to_folder)
                if success:
                    log_debug(f"event_processor: File created based on datetime extraction from {src_path}")
                if target_image_folder and wait_time and image_save_folder:
                    process_images(event_type, src_path, target_image_folder, wait_time, image_save_folder, log_debug)
            
            elif event_type in ['wf_info_created', 'wf_info_modified']:
                # wf_info 파일이 생성되거나 수정되었을 때 처리하는 로직입니다.
                log_debug(f"event_processor: Processing wf_info event: {event_type} for file: {src_path}")
                if target_image_folder and wait_time and image_save_folder:
                    process_images(event_type, src_path, target_image_folder, wait_time, image_save_folder, log_debug)

        except Exception as e:
            # 이벤트 처리 중 오류가 발생하면 로그에 기록합니다.
            log_debug(f"event_processor: Error processing event {event}: {str(e)}")
