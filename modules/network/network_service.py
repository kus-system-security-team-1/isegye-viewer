class NetworkService:
    def __init__(self, config):
        self.config = config
        self.lib = config["lib"]["Network"]

    def block_process_traffic(self, pid):
        self.lib.blockProcessTraffic(pid)

    def unblock_process_traffic(self, pid):
        self.lib.unblockProcessTraffic(pid)
