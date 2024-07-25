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

def extract_file_info(filename):
    match = re.match(r"(\d{8}_\d{6})_([A-Z0-9.]+)_([A-Z0-9]+)_", filename)
    if match:
        datetime_str, compare_str, extract_str = match.groups()
        return datetime_str, compare_str, extract_str
    return None, None, None

def create_file_based_on_datetime(file_path, log_debug, log_event, save_to_folder):
    encodings = ['cp949', 'utf-8', 'latin1']  # 시도할 인코딩 목록
    content = None
    
    for encoding in encodings:
        try:
            log_debug(f"event_processor: Trying to read file with {encoding} encoding: {file_path}")
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
                log_debug(f"event_processor: File content read successfully with {encoding} encoding.")
                break  # 성공하면 반복을 중단
        except Exception as e:
            log_debug(f"event_processor: Error reading file with {encoding} encoding: {str(e)}")
    
    if content is None:
        log_debug(f"event_processor: Failed to read file with all attempted encodings: {file_path}")
        return False
    
    # 파일 내용에서 Date and Time 추출
    match = re.search(r"Date and Time:\s+(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\s+[APM]{2})", content)
    if match:
        log_debug(f"event_processor: Match found: {match.group(1)}")
        datetime_str = datetime.strptime(match.group(1), '%m/%d/%Y %I:%M:%S %p').strftime('%Y%m%d_%H%M%S')
        _, file_name = os.path.split(file_path)
        
        wf_info_dir = os.path.join(save_to_folder, 'wf_info')
        if not os.path.exists(wf_info_dir):
            os.makedirs(wf_info_dir)
            log_debug(f"event_processor: Created directory {wf_info_dir}")

        new_file_name = f"{datetime_str}_{file_name.rsplit('.', 1)[0]}.na"
        new_file_path = os.path.join(wf_info_dir, new_file_name)
        
        with open(new_file_path, 'w', encoding='cp949') as new_file:
            new_file.write("")
        
        log_debug(f"event_processor: Created empty file {new_file_path} based on {file_path}")
        log_event("event_processor: File Created", new_file_path)
        return True
    else:
        log_debug(f"event_processor: No Date and Time found in {file_path}")
        return False

def replace_text_in_files(wf_file_info, target_folder, log_debug, log_event):
    wf_datetime, wf_compare, wf_extract = wf_file_info
    log_debug(f"event_processor: Attempting to replace text in files in {target_folder} matching {wf_file_info}")
    for root, _, files in os.walk(target_folder):
        for filename in files:
            if wf_datetime in filename and wf_compare in filename:
                old_path = os.path.join(root, filename)
                new_filename = filename.replace("#1", wf_extract)
                new_path = os.path.join(root, new_filename)
                if "#1" in filename:
                    log_debug(f"event_processor: Renaming {old_path} to {new_path}")
                    os.rename(old_path, new_path)
                    log_event("event_processor: File Renamed", f"{old_path} -> {new_filename}")

def images_to_pdf(image_paths, output_folder, base_name, log_debug):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        log_debug(f"event_processor: Created output folder: {output_folder}")

    pdf_path = os.path.join(output_folder, f"{base_name}.pdf")
    log_debug(f"event_processor: PDF path: {pdf_path}")

    try:
        c = canvas.Canvas(pdf_path, pagesize=letter)
        for image_path in sorted(image_paths, key=lambda x: int(re.search(r'\d+$', os.path.splitext(x)[0]).group())):
            img = Image.open(image_path)
            img_width, img_height = img.size

            # 페이지 크기를 이미지 크기로 설정
            c.setPageSize((img_width, img_height))

            # 이미지를 PDF에 추가
            c.drawImage(image_path, 0, 0, img_width, img_height)
            c.showPage()

        c.save()
        log_debug(f"event_processor: PDF created at {pdf_path}")
    except Exception as e:
        log_debug(f"event_processor: Error creating PDF: {str(e)}")

def process_images(event_type, src_path, target_image_folder, wait_time, image_save_folder, log_debug):
    # wf_info 폴더 대상만 실행하도록 수정
    if 'wf_info' not in src_path:
        log_debug(f"event_processor: Ignored {event_type} event for non-wf_info path: {src_path}")
        return
    
    # 정규 표현식 패턴 정의
    datetime_pattern = r'^(\d{8}_\d{6})'
    specific_pattern = r'\d+_\d+_(\w+\.\w+_C\dW\d+)_'
    
    log_debug(f"event_processor: Processing images for {event_type} event: {src_path}")

    filename = os.path.basename(src_path)       # 파일 경로에서 파일 이름만 추출
    basename = os.path.splitext(filename)[0]    # 파일 이름에서 확장자를 제외한 이름만 가져오기

    log_debug(f"event_processor: Extracted filename: {filename}")
    
    try:
        datetime_match = re.match(datetime_pattern, basename)
        datetime_str = datetime_match.group(1) if datetime_match else None
    except ValueError as e:
        log_debug(f"event_processor: Error extracting datetime and pattern from filename: {str(e)}")
        return

    specific_pattern_match = re.search(specific_pattern, basename)
    specific_pattern_2 = specific_pattern_match.group(1) if specific_pattern_match else None
    
    log_debug(f"event_processor: Extracted patterns: {datetime_str}, {specific_pattern_2}")

    log_debug(f"event_processor: Waiting for {wait_time} seconds before processing images.")
    time.sleep(int(wait_time))

    matching_images = []
    for root, _, files in os.walk(target_image_folder):
        for file in files:
            if datetime_str in file and specific_pattern_2 in file:
                matching_images.append(os.path.join(root, file))

    if matching_images:
        log_debug(f"event_processor: Found {len(matching_images)} matching images. Converting to PDF.")
        common_prefix = os.path.commonprefix([os.path.splitext(f)[0] for f in matching_images])
        base_name = common_prefix.rstrip('_0123456789')
        images_to_pdf(matching_images, image_save_folder, base_name, log_debug)
    else:
        log_debug("event_processor: No matching images found.")

def event_processor(event_queue, log_event, log_debug, perf_monitor, dest_folder, regex_folders, base_date_folder, save_to_folder, target_compare_folders):
    while True:
        try:
            event = event_queue.get(timeout=1)
            log_debug(f"event_processor: Received event: {event}")
        except queue.Empty:
            continue
        try:
            event_type, src_path, *extra = event
            
            # Ensure extra list has enough elements
            target_image_folder = extra[0] if len(extra) > 0 else None
            wait_time = extra[1] if len(extra) > 1 else None
            image_save_folder = extra[2] if len(extra) > 2 else None

            log_debug(f"event_processor: Processing event of type '{event_type}' for file: {src_path}")

            if event_type in ['created', 'modified', 'deleted', 'moved']:
                perf_monitor.log_performance()

            if event_type in ['created', 'modified']:
                matched = False
                for pattern, subfolder in regex_folders.items():
                    if re.search(pattern, os.path.basename(src_path)):
                        dest_path = normalize_path(os.path.join(dest_folder, subfolder, os.path.basename(src_path)))
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        if normalize_path(src_path) != normalize_path(dest_path):
                            try:
                                shutil.copy2(src_path, dest_path)
                                log_event(f"event_processor: File {event_type} detected. Copied to {dest_path}")
                                log_debug(f"event_processor: File {event_type} detected. Copied to {dest_path}")
                            except Exception as e:
                                log_debug(f"event_processor: Error copying file {src_path} to {dest_path}: {str(e)}")
                        else:
                            log_debug(f"event_processor: Source and destination paths are the same: {src_path}")
                        matched = True
                        break
                if not matched:
                    log_event(f"event_processor: File {event_type} detected but no matching regex pattern found for copying.")
                    log_debug(f"event_processor: File {event_type} detected but no matching regex pattern found for copying.")
                
                # Here, ensure create_file_based_on_datetime is called correctly
                if event_type in ['created', 'modified'] and base_date_folder in src_path:
                    success = create_file_based_on_datetime(src_path, log_debug, log_event, save_to_folder)
                    if success:
                        log_debug(f"event_processor: File created based on datetime extraction from {src_path}")

            elif event_type == 'deleted':
                log_event(f"event_processor: deleted", src_path)
                log_debug(f"event_processor: Processed 'deleted' event for file: {src_path}")
            elif event_type == 'moved':
                dest_path = extra[0] if len(extra) > 0 else None
                log_event(f"event_processor: moved", src_path, dest_path)
                log_debug(f"event_processor: Processed 'moved' event from {src_path} to {dest_path}")

            elif event_type in ['base_date_created', 'base_date_modified']:
                log_debug(f"event_processor: Processing base date event: {event_type} for file: {src_path}")
                success = create_file_based_on_datetime(src_path, log_debug, log_event, save_to_folder)
                if success:
                    log_debug(f"event_processor: File created based on datetime extraction from {src_path}")
                if target_image_folder and wait_time and image_save_folder:
                    process_images(event_type, src_path, target_image_folder, wait_time, image_save_folder, log_debug)

            elif event_type in ['wf_info_created', 'wf_info_modified']:
                log_debug(f"event_processor: Processing wf_info event: {event_type} for file: {src_path}")
                if target_image_folder and wait_time and image_save_folder:
                    process_images(event_type, src_path, target_image_folder, wait_time, image_save_folder, log_debug)

        except Exception as e:
            log_debug(f"event_processor: Error processing event {event}: {str(e)}")
