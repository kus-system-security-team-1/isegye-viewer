from modules.pe.pe_service import PEService


class PEController:
    def __init__(self, config, view=None, app_module=None):
        self.view = view
        self.config = config
        self.service = PEService(config)

    def calculate_entropy(self, pe_name):
        try:
            entropy = self.service.calculate_entropy(pe_name)
            return entropy
        except Exception as e:
            print(f"Error : {e}")
