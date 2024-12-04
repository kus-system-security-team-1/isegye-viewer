class PEWindow:
    def __init__(self):
        super().__init__()
        self.controller = None
        self.app_module = None
        self.init_ui()

    def set_app_module(self, app_module):
        self.app_module = app_module
        self.init_ui()

    def init_ui(self):
        if self.app_module:
            self.controller = self.app_module.get_controller(
                "PEController"
            )
        if not self.controller:
            return
