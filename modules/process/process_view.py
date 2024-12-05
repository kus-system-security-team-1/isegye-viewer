from common.base_window import BaseWindow


class ProcessWindow(BaseWindow):
    def __init__(self):
        super().__init__()

    def init_ui(self):
        super().init_ui("ProcessController")
