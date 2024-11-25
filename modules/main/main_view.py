from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
import resources.resources_rc


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/main_window.ui", self)
        self.controller = None
        self.app_module = None
        self.page_widget.setCurrentIndex(0)
        self.btn_process.setChecked(True)
        self.init_ui()

    def set_app_module(self, app_module):
        self.app_module = app_module
        self.init_ui()

    def init_ui(self):
        if self.app_module:
            self.controller = self.app_module.get_controller("MainController")
        if not self.controller:
            return
        self.btn_process.clicked.connect(
            lambda: self.controller.show_subpage(0)
        )
        self.btn_history.clicked.connect(
            lambda: self.controller.show_subpage(1)
        )
