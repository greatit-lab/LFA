from PySide6.QtGui import QIcon  # 트레이 아이콘을 설정하기 위해 필요한 클래스입니다.
from PySide6.QtWidgets import QSystemTrayIcon, QMenu  # 시스템 트레이 아이콘과 메뉴를 설정하기 위한 클래스입니다.
import os  # 운영체제와 상호작용하기 위한 모듈을 불러옵니다.
import sys  # 파이썬 인터프리터와 상호작용하기 위한 모듈을 불러옵니다.

# 리소스 파일의 절대 경로를 반환하는 함수입니다. PyInstaller와 같은 도구로 패키징할 때도 경로를 올바르게 참조할 수 있도록 합니다.
def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    주어진 상대 경로를 절대 경로로 변환하여 반환합니다. PyInstaller로 패키징할 때 파일 경로를 올바르게 참조할 수 있도록 합니다.
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# 시스템 트레이 아이콘을 설정하고 실행하는 함수입니다.
def run_tray_icon(app):
    # 트레이 아이콘에 사용할 이미지의 경로를 설정합니다.
    icon_path = resource_path("resources/icons/icon.png")  
    # 시스템 트레이 아이콘을 초기화합니다. 아이콘 이미지와 애플리케이션 객체를 전달합니다.
    tray_icon = QSystemTrayIcon(QIcon(icon_path), app)
    # 트레이 아이콘에 마우스를 올렸을 때 표시될 툴팁(설명)을 설정합니다.
    tray_icon.setToolTip("LogFusion Agent")

    # "Show" 메뉴 항목을 클릭했을 때 실행되는 함수입니다.
    def show_window():
        app.show_window()  # 애플리케이션 창을 화면에 표시합니다.

    # "Run" 메뉴 항목을 클릭했을 때 실행되는 함수입니다.
    def start_monitoring():
        app.start_monitoring()  # 애플리케이션에서 모니터링을 시작합니다.
        update_tray_menu()  # 트레이 메뉴를 업데이트합니다.

    # "Stop" 메뉴 항목을 클릭했을 때 실행되는 함수입니다.
    def stop_monitoring():
        app.stop_monitoring()  # 애플리케이션에서 모니터링을 중지합니다.
        update_tray_menu()  # 트레이 메뉴를 업데이트합니다.

    # "Quit" 메뉴 항목을 클릭했을 때 실행되는 함수입니다.
    def quit_app():
        app.quit_app()  # 애플리케이션을 종료합니다.

    # 트레이 아이콘의 메뉴를 업데이트하는 함수입니다.
    def update_tray_menu():
        menu.clear()  # 기존 메뉴 항목들을 모두 제거합니다.
        # "Show" 메뉴 항목을 추가하고, 클릭 시 show_window 함수가 실행되도록 설정합니다.
        show_action = menu.addAction("Show")
        show_action.triggered.connect(show_window)
        # "Run" 메뉴 항목을 추가하고, 현재 애플리케이션 상태에 따라 활성화 여부를 설정합니다.
        run_action = menu.addAction("Run")
        run_action.setEnabled(app.monitoring_controls.status_label.text() in ["Status: Idle", "Status: Stopped"])
        run_action.triggered.connect(start_monitoring)
        # "Stop" 메뉴 항목을 추가하고, 현재 애플리케이션 상태에 따라 활성화 여부를 설정합니다.
        stop_action = menu.addAction("Stop")
        stop_action.setEnabled(app.monitoring_controls.status_label.text() == "Status: Monitoring")
        stop_action.triggered.connect(stop_monitoring)
        # "Quit" 메뉴 항목을 추가하고, 클릭 시 quit_app 함수가 실행되도록 설정합니다.
        quit_action = menu.addAction("Quit")
        quit_action.setEnabled(app.monitoring_controls.status_label.text() in ["Status: Idle", "Status: Stopped"])
        quit_action.triggered.connect(quit_app)
        # 트레이 아이콘에 설정된 메뉴를 적용합니다.
        tray_icon.setContextMenu(menu)

    # 시스템 트레이 아이콘의 메뉴를 초기화합니다.
    menu = QMenu()
    # 트레이 아이콘의 초기 메뉴를 설정합니다.
    update_tray_menu()
    # 트레이 아이콘에 설정된 메뉴를 적용합니다.
    tray_icon.setContextMenu(menu)
    # 트레이 아이콘을 화면에 표시합니다.
    tray_icon.show()
    return tray_icon  # 설정된 트레이 아이콘을 반환합니다.
