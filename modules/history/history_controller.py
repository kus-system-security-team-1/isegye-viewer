from modules.history.history_service import HistoryService
from modules.history.history_view import HistoryWindow


class HistoryController:
    def __init__(self, config, view=None):
        self.view = HistoryWindow()
        self.config = config
        self.service = HistoryService(config)
