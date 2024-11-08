from modules.process.process_service import ProcessService
from modules.process.process_view import ProcessWindow


class ProcesssController:
    def __init__(self, config):
        self.view = ProcessWindow()
        self.config = config
        self.service = ProcessService(config)
