from modules.pe.pe_service import PEService


class PEController:
    def __init__(self, config, view=None, app_module=None):
        self.view = view
        self.config = config
        self.service = PEService(config)

    def detect_entropy(self, pe_name):
        try:
            entropy = self.service.calculate_entropy(pe_name)
            level_entropy = self.service.detect_entropy_level(entropy)
            entropy = round(entropy, 1)

            return entropy, level_entropy
        except Exception as e:
            print(f"Error : {e}")
