from modules.history.history_service import HistoryService


class HistoryController:
    def __init__(self, config, view=None, app_module=None):
        self.view = view
        self.config = config
        self.service = HistoryService(config)

    def log_process_times_to_file(self, pid, logFilePath):
        data = self.service.log_process_times_to_file(pid, logFilePath)
        print(data)

    def write_file_time_to_log(self, pid, logFile):
        data = self.service.write_file_time_to_log(pid, logFile)
        print(data)
