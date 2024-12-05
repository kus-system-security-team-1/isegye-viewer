from modules.history.history_service import HistoryService

# from modules.history.history_view import HistoryWindow


class HistoryController:
    def __init__(self, config, view=None, app_module=None):
        self.view = view
        self.config = config
        self.service = HistoryService(config)
