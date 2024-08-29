import os
import pandas as pd
from upload.db_info import get_db_engine

class PreAlignHandler:
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
        # PreAlign 데이터 처리를 위한 로직을 추가하세요.
        pass

    def upload_to_mysql(self, df):
        engine = get_db_engine()
        df.to_sql('prealign', con=engine, if_exists='append', index=False)
