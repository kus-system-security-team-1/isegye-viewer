from PyQt5.QtWidgets import QMessageBox
from modules.main.main_service import MainService
from modules.main.main_view import MainWindow


class MainController:
    def __init__(self, config):
        self.view = MainWindow()
        self.config = config
        self.service = MainService(config)

    def handle_button_click(self):
        message = self.service.process_data("Button clicked")
        QMessageBox.information(self.view, "Info", message)
