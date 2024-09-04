import sys  # 파이썬 인터프리터와 상호작용하기 위한 모듈을 불러옵니다.
import os  # 운영체제와 상호작용하기 위한 모듈을 불러옵니다.
import psutil  # 시스템 및 프로세스 정보를 가져오기 위한 모듈을 불러옵니다.
from PySide6.QtWidgets import QApplication, QDialog  # PySide6 라이브러리에서 GUI 관련 클래스를 불러옵니다.
from ui.app import MonitorApp  # 사용자 정의 애플리케이션 UI를 불러옵니다.
from ui.eqpid_input import EqpidInputDialog  # EQPID 입력을 위한 다이얼로그를 불러옵니다.
from config import load_settings, save_settings, load_eqpid, save_eqpid  # 설정 파일 관련 함수들을 불러옵니다.
from logger import setup_event_logging, add_debug_logging, update_logging_config  # 로그 설정 관련 함수를 불러옵니다.

# 애플리케이션 전역 설정을 관리하는 클래스입니다.
class AppContext:
    def __init__(self, base_dir):
        # EQPID(장비 ID)를 설정 파일에서 불러옵니다.
        self.eqpid = load_eqpid()
        # 설정 파일에서 다양한 설정을 불러옵니다.
        self.monitored_folders, self.dest_folder, self.regex_folders, self.exclude_folders, self.base_date_folder, self.target_compare_folders,self.target_image_folder, self.wait_time, self.image_save_folder, self.wafer_flat_data_path, self.prealign_data_path, self.image_data_path, slef.error_data_path, self.event_data_path, self.wave_data_path = load_settings()
        self.base_dir = base_dir  # 로그를 저장할 기본 디렉토리를 설정합니다.
        self.logger = None  # 로거를 초기화하기 전까지는 None으로 설정합니다.

    def initialize_logger(self):
        # 로거가 아직 초기화되지 않았다면, 로거를 초기화합니다.
        if self.logger is None:
            setup_event_logging(self.base_dir)  # 이벤트 로그를 설정합니다.
            add_debug_logging(self.base_dir)  # 디버그 로그를 설정합니다.

    def save_settings(self):
        # 현재 애플리케이션의 설정을 설정 파일에 저장합니다.
        save_settings(
            self.monitored_folders,
            self.dest_folder,
            self.regex_folders,
            self.exclude_folders,
            self.base_date_folder,
            self.target_compare_folders,
            self.target_image_folder,
            self.wait_time,
            self.image_save_folder,
            self.wafer_flat_data_path,
            self.prealign_data_path,
            self.image_data_path,
            slef.error_data_path,
            self.event_data_path,
            self.wave_data_path
        )

# 프로그램의 중복 실행을 방지하기 위해 다른 인스턴스가 실행 중인지 확인하는 함수입니다.
def is_another_instance_running(pid_file):
    if os.path.isfile(pid_file):  # PID 파일이 존재하는지 확인합니다.
        with open(pid_file, 'r') as f:
            pid = int(f.read())  # 파일에서 PID를 읽어옵니다.
        if psutil.pid_exists(pid):  # 해당 PID가 현재 실행 중인 프로세스인지 확인합니다.
            return True  # 이미 실행 중이라면 True를 반환합니다.
        else:
            os.remove(pid_file)  # 실행 중이지 않다면 PID 파일을 삭제합니다.
    return False  # 다른 인스턴스가 실행 중이지 않다면 False를 반환합니다.

# 현재 프로세스 ID를 기록하는 파일을 생성하는 함수입니다.
def create_pid_file(pid_file):
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))  # 현재 프로세스의 ID를 파일에 기록합니다.

# 프로세스 ID 파일을 삭제하는 함수입니다.
def remove_pid_file(pid_file):
    if os.path.isfile(pid_file):  # PID 파일이 존재하면 삭제합니다.
        os.remove(pid_file)

# 프로그램의 시작점입니다. 메인 프로그램이 여기서 실행됩니다.
if __name__ == "__main__":
    PID_FILE = 'program.pid'  # PID 파일의 이름을 설정합니다.
    
    # 다른 인스턴스가 실행 중인지 확인합니다.
    if is_another_instance_running(PID_FILE):
        print("Another instance of the program is already running.")
        sys.exit(1)  # 이미 실행 중이라면 프로그램을 종료합니다.
    
    create_pid_file(PID_FILE)  # PID 파일을 생성하여 현재 프로세스 ID를 기록합니다.

    app = QApplication(sys.argv)  # PySide6 애플리케이션 객체를 생성합니다.

    eqpid = load_eqpid()  # 설정 파일에서 EQPID를 불러옵니다.
    
    # EQPID가 설정되지 않았다면, 사용자에게 입력을 요청하는 다이얼로그를 표시합니다.
    if eqpid is None:
        dialog = EqpidInputDialog()
        if dialog.exec_() == QDialog.Accepted:  # type: ignore # 사용자가 EQPID를 입력하고 확인을 누르면,
            eqpid = dialog.get_eqpid()
            save_eqpid(eqpid)  # EQPID를 설정 파일에 저장합니다.
        else:
            sys.exit(0)  # 사용자가 취소를 누르면 프로그램을 종료합니다.

    base_dir = os.path.join(os.getcwd(), 'EventLog')  # 현재 작업 디렉토리에 'EventLog' 폴더를 만듭니다.
    app_context = AppContext(base_dir)  # 애플리케이션 컨텍스트를 초기화합니다.
    app_context.initialize_logger()  # 로거를 초기화합니다.
    
    main_window = MonitorApp(app_context, base_dir)  # 메인 애플리케이션 창을 생성합니다.

    # 프로그램 종료 시 실행되는 함수입니다.
    def on_close():
        app_context.save_settings()  # 설정을 저장합니다.
        remove_pid_file(PID_FILE)  # PID 파일을 삭제합니다.
        sys.exit(0)  # 프로그램을 종료합니다.

    app.aboutToQuit.connect(on_close)  # 애플리케이션이 종료될 때 on_close 함수를 호출합니다.
    main_window.show()  # 메인 윈도우를 화면에 표시합니다.
    sys.exit(app.exec())  # 애플리케이션의 메인 이벤트 루프를 실행합니다.
