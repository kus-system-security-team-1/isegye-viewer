from PyQt5.QtWidgets import QMessageBox
from modules.main.main_service import MainService
from modules.main.main_view import MainWindow


class MainController:
    def __init__(self, config):
        self.view = MainWindow()    
        self.config = config
        self.service = MainService(config)

    def show_subpage(self, index): # 하위 페이지 보여주기
        self.view.page_widget.setCurrentIndex(index)
        

    
