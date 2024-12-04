import os
import importlib
import lib.isegye_viewer_core as isegye_viewer_core


class AppModule:
    def __init__(self):
        self.controllers = {}
        self.lib = {}
        for class_name in dir(isegye_viewer_core):
            if "__" not in class_name:
                cls = getattr(isegye_viewer_core, class_name)
                if isinstance(cls, type):
                    try:
                        self.lib[class_name] = cls()
                    except Exception as e:
                        print(f"Failed to initialize {class_name}: {e}")

    def init_modules(self, main_window=None):
        self._load_modules("modules.main", "Controller", main_window)
        self._load_modules("modules.process", "Controller", main_window)
        self._load_modules("modules.history", "Controller", main_window)

    def _load_modules(self, package_path, class_suffix, main_window=None):
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
                        instance = controller_class(
                            config={"lib": self.lib}, view=main_window
                        )
                        self.controllers[attribute_name] = instance

    def get_controller(self, controller_name):
        return self.controllers.get(controller_name, None)
