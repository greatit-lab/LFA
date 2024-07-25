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

def replace_text_in_files(wf_file_info, target_folder, log_debug, log_event):
    wf_datetime, wf_compare, wf_extract = wf_file_info
    log_debug(f"Attempting to replace text in files in {target_folder} matching {wf_file_info}")
    for root, _, files in os.walk(target_folder):
        for filename in files:
            if wf_datetime in filename and wf_compare in filename:
                old_path = os.path.join(root, filename)
                new_filename = filename.replace("#1", wf_extract)
                new_path = os.path.join(root, new_filename)
                if "#1" in filename:
                    log_debug(f"Renaming {old_path} to {new_path}")
                    os.rename(old_path, new_path)
                    log_event("File Renamed", f"{old_path} -> {new_filename}")

def create_file_based_on_datetime(file_path, log_debug, log_event, save_to_folder):
    try:
        log_debug(f"Reading file for datetime extraction: {file_path}")
        with open(file_path, 'r', encoding='cp949') as file:
            content = file.read()
        
        match = re.search(r"Date and Time:\s+(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\s+[APM]{2})", content)
        if match:
            log_debug(f"Match found: {match.group(1)}")
            datetime_str = datetime.strptime(match.group(1), '%m/%d/%Y %I:%M:%S %p').strftime('%Y%m%d_%H%M%S')
            _, file_name = os.path.split(file_path)
            
            wf_info_dir = os.path.join(save_to_folder, 'wf_info')
            if not os.path.exists(wf_info_dir):
                os.makedirs(wf_info_dir)
                log_debug(f"Created directory {wf_info_dir}")

            new_file_name = f"{datetime_str}_{file_name.rsplit('.', 1)[0]}.na"
            new_file_path = os.path.join(wf_info_dir, new_file_name)
            
            with open(new_file_path, 'w', encoding='cp949') as new_file:
                new_file.write("")
            
            log_debug(f"Created empty file {new_file_path} based on {file_path}")
            log_event("File Created", new_file_path)
            return True
        else:
            log_debug(f"No Date and Time found in {file_path}")
            return False
    except Exception as e:
        log_debug(f"Error creating file based on {file_path}: {str(e)}")
        return False

def images_to_pdf(image_paths, output_folder, base_name):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_path = os.path.join(output_folder, f"{base_name}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)

    for image_path in image_paths:
        img = Image.open(image_path)
        img_width, img_height = img.size

        # 페이지 크기를 이미지 크기로 설정
        c.setPageSize((img_width, img_height))

        # 이미지를 PDF에 추가
        c.drawImage(image_path, 0, 0, img_width, img_height)
        c.showPage()

    c.save()

def process_images(event_type, src_path, target_image_folder, wait_time, save_to_folder):
    log_debug(f"Processing images for {event_type} event: {src_path}")

    filename = os.path.basename(src_path)
    datetime_str, specific_pattern = filename.split('_')[:2]

    log_debug(f"Waiting for {wait_time} seconds before processing images.")
    time.sleep(wait_time)

    matching_images = []
    for root, _, files in os.walk(target_image_folder):
        for file in files:
            if specific_pattern in file and datetime_str in file:
                matching_images.append(os.path.join(root, file))

    if matching_images:
        log_debug(f"Found {len(matching_images)} matching images. Converting to PDF.")
        base_name = f"{datetime_str}_{specific_pattern}"
        images_to_pdf(matching_images, save_to_folder, base_name)
    else:
        log_debug("No matching images found.")

def event_processor(event_queue, log_event, log_debug, perf_monitor, dest_folder, regex_folders, base_date_folder, save_to_folder, target_compare_folders):
    while True:
        try:
            event = event_queue.get(timeout=1)
            log_debug(f"Processing event: {event}")
        except queue.Empty:
            continue
        try:
            event_type, src_path, *extra = event
            target_image_folder = extra[0] if extra else None
            wait_time = extra[1] if extra else None

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
                                log_event(event_type, src_path, dest_path)
                                log_debug(f"File {event_type} and copied to {dest_path}")
                            except Exception as e:
                                log_debug(f"Error copying file {src_path} to {dest_path}: {str(e)}")
                        else:
                            log_debug(f"Source and destination are the same: {src_path}")
                        matched = True
                        break
                if not matched:
                    log_event(event_type, src_path)
                    log_debug(f"File {event_type} but no matching regex pattern found for copying")

            elif event_type == 'deleted':
                log_event("deleted", src_path)
                log_debug(f"Processing event: deleted for {src_path}")
            elif event_type == 'moved':
                log_event("moved", src_path, dest_path)

            elif event_type in ['base_date_created', 'base_date_modified']:
                create_file_based_on_datetime(src_path, log_debug, log_event, save_to_folder)
                if target_image_folder and wait_time:
                    process_images(event_type, src_path, target_image_folder, wait_time, save_to_folder)

        except Exception as e:
            log_debug(f"Error processing event {event}: {str(e)}")
