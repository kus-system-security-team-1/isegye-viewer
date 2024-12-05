from PyQt5 import uic


class BaseWindow:
    def __init__(self, ui_file=None):
        super().__init__()
        self.controller = None
        self.app_module = None

        if ui_file:
            uic.loadUi(ui_file, self)

    def set_app_module(self, app_module):
        self.app_module = app_module
        self.init_ui()

    def init_ui(self, controller_name=None):
        if self.app_module and controller_name:
            self.controller = self.app_module.get_controller(controller_name)
        if not self.controller:
            return
