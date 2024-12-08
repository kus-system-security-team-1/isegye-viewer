from modules.history.history_service import HistoryService
from pathlib import Path
from datetime import datetime


class HistoryController:
    def __init__(self, config, view=None, app_module=None):
        self.view = view
        self.config = config
        self.service = HistoryService(config)

    def log_process_times_to_file(self, pid, process):
        current_day = datetime.now().strftime("%Y-%m-%d")
        folder_name = current_day
        file_name = process.split(".exe")[0] + ".txt"
        logFilePath = Path(f"./log/history/{folder_name}")
        logFilePath.mkdir(parents=True, exist_ok=True)
        file_path = logFilePath / file_name
        self.service.log_process_times_to_file(pid, str(file_path))

    def write_file_time_to_log(self, pid, logFile):
        data = self.service.write_file_time_to_log(pid, logFile)
        print(data)
