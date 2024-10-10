from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/main_window.ui", self)
        self.controller = None
        self.app_module = None
        self.init_ui()

    def set_app_module(self, app_module):
        self.app_module = app_module
        self.init_ui()

    def init_ui(self):
        if self.app_module:
            self.controller = self.app_module.get_controller("MainController")
        if not self.controller:
            return
        self.pushButton.clicked.connect(
            self.controller.handle_button_click
        )
