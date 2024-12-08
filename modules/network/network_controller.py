from modules.network.network_service import NetworkService


class NetworkController:
    def __init__(self, config, view=None, app_module=None):
        self.view = view
        self.config = config
        self.service = NetworkService(config)

    def block_process_traffic(self, pid):
        self.service.block_process_traffic(pid)
        print("Call block process traffic")

    def unblock_process_traffic(self, pid):
        self.service.unblock_process_traffic(pid)
        print("Call unblock process traffic")
