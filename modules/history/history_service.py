class HistoryService:
    def __init__(self, config):
        self.config = config
        self.lib = config["lib"]["History"]

    def get_account_name_of_process(self, pid):
        return self.lib.getAccountNameOfProcess(pid)

    def add_process_log_to_file(self, pid):
        return self.lib.addProcessLogToFile(pid)

    def log_process_times_to_file(self, pid, logFilePath):
        return self.lib.LogProcessTimesToFile(pid, logFilePath)

    def write_file_time_to_log(self, pid, logFile):
        return self.lib.writeFileTimeToLog(pid, logFile)
