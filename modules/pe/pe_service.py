class PEService:
    def __init__(self, config):
        self.config = config
        self.lib = config["lib"]["PE"]

    def calculate_entropy(self, pe_name):
        return self.lib.calculateEntropy(pe_name)

    def detect_entropy_level(self, entropy):
        return self.lib.detectEntropyLevel(entropy)
