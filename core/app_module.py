import os
import importlib


class AppModule:
    def __init__(self):
        self.controllers = {}

    def init_modules(self):
        self._load_modules("modules.main", "Controller")
        self._load_modules("modules.process", "Controller")

    def _load_modules(self, package_path, class_suffix):
        package = importlib.import_module(package_path)
        package_dir = package.__path__[0]

        for filename in os.listdir(package_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]
                module = importlib.import_module(
                    f"{package_path}.{module_name}"
                )
                for attribute_name in dir(module):
                    if attribute_name.endswith(class_suffix):
                        controller_class = getattr(module, attribute_name)
                        instance = controller_class(config={})
                        self.controllers[attribute_name] = instance

    def get_controller(self, controller_name):
        return self.controllers.get(controller_name, None)
