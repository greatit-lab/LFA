import os
import re
import pandas as pd
from upload.db_info import get_db_engine

class WaferFlatHandler:
    def __init__(self, folder_to_track):
        self.folder_to_track = folder_to_track
        self.processed_files = set()

    def on_modified(self, event):
        for filename in os.listdir(self.folder_to_track):
            file_path = os.path.join(self.folder_to_track, filename)
            if os.path.isfile(file_path) and file_path not in self.processed_files:
                self.process_file(file_path)
                self.processed_files.add(file_path)

    def process_file(self, file_path):
        with open(file_path, 'r', encoding='cp949') as file:
            log_data = file.read()

        lines = log_data.strip().split('\n')
        data = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()

        wafer_id = data.get('Wafer ID')
        wafer_number = int(re.search(r'W(\d+)', wafer_id).group(1)) if wafer_id else None
        data['Date and Time'] = pd.to_datetime(data.get('Date and Time'), errors='coerce')

        expected_header = [
            'Point#','MSE','T1','GOF','HPL','X','Y','DieX','DieY','DieRow','DieCol','DieNum','DiePointTag','Z','SRVISZ',
            'T1_noCal','CU_HT_noCal','T1_CAL','x1','RgnHeight11','RgnHeight16','RgnHeight17','RgnBWidth17'
        ]

        header_line = None
        for idx, line in enumerate(lines):
            if line.startswith('Point#'):
                header_line = line
                header_idx = idx
                break

        def clean_header(header):
            header = header.replace('(no Cal)', '_noCal')
            header = header.replace('(mm)', '').strip()
            header = header.replace('(탆)', '').strip()
            header = header.replace('(Die X)', 'DieX').replace('(Die Y)', 'DieY')
            return header

        if header_line:
            headers = [clean_header(h.strip()) for h in header_line.split(',')]
            additional_lines = lines[header_idx + 1:]
            additional_data = []
            for line in additional_lines:
                values = [item.strip() for item in line.split(',')]
                row = {
                    'CassetteRCP': data.get('Cassette Recipe Name'),
                    'StageRCP': data.get('Stage Recipe Name'),
                    'StageGroup': data.get('Stage Group Name'),
                    'LotID': data.get('Lot ID'),
                    'WaferID': wafer_number,
                    'DateTime': data.get('Date and Time'),
                    'Film': data.get('Film Name'),
                    'Point': int(values[0]) if len(values) > 0 else None,
                    'MSE': float(values[1]) if len(values) > 1 else None,
                }

                for header in expected_header[2:]:
                    if header in headers:
                        index = headers.index(header)
                        if index < len(values):
                            if header in ['DieRow', 'DieCol', 'DieNum', 'DiePointTag']:
                                row[header] = int(values[index]) if values[index] else None
                            else:
                                row[header] = float(values[index]) if values[index] else None
                        else:
                            row[header] = None
                    else:
                        row[header] = None

                additional_data.append(row)

            df = pd.DataFrame(additional_data)
            print(df)

            self.upload_to_mysql(df)
            os.remove(file_path)
            print(f"파일 {file_path} 이(가) 삭제되었습니다.")

    def upload_to_mysql(self, df):
        engine = get_db_engine()
        df.to_sql('wf', con=engine, if_exists='append', index=False)
