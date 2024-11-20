from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
import ui.resources_rc


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/main_window.ui", self)
        self.controller = None
        self.app_module = None
        self.mainstackedWidget.setCurrentIndex(0)
        self.page_widget.setCurrentIndex(0)
        self.init_ui()

    def set_app_module(self, app_module):
        self.app_module = app_module
        self.init_ui()

    def init_ui(self):
        if self.app_module:
            self.controller = self.app_module.get_controller("MainController")
        if not self.controller:
            return # 이거 컨트롤러가 없어서 테스트 해보려고 해도 안되는데 어케 해결함
        self.mbtn_process_info.clicked.connect(
            lambda: self.controller.show_subpage(0) # 메인화면에서 다음 페이지로 넘기기
        )
    
        
