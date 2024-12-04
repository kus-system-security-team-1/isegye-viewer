from modules.pe.pe_service import PEService
from modules.pe.pe_view import PEWindow


class PEController:
    def __init__(self, config, view=None):
        self.view = PEWindow()
        self.config = config
        self.service = PEService(config)
