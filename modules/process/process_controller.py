from modules.process.process_service import ProcessService

# from modules.process.process_view import ProcessWindow


class ProcesssController:
    def __init__(self, config, view=None, app_module=None):
        self.view = view
        self.config = config
        self.service = ProcessService(config)

    def get_all_processes(self):
        data = self.service.get_all_processes()
        print(data)
        return data

    # def show_network_io(self):
    #     todo: get pid from other service
    #     data = self.service.show_network_io(pid)

    def show_network_packets(self):
        data = self.service.show_network_packets()
        return data
