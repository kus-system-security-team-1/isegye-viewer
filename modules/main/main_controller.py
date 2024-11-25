from modules.main.main_service import MainService


class MainController:
    def __init__(self, config, view=None):
        self.view = view
        self.config = config
        self.service = MainService(config)
        print(f"MainController initialized with view: {self.view}")

    def show_subpage(self, index):
        if self.view:
            self.view.page_widget.setCurrentIndex(index)
