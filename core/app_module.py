import os
import importlib


class AppModule:
    def __init__(self):
        self.controllers = {}

    def init_modules(self):
        # 특정 디렉터리를 스캔하여 모든 컨트롤러를 자동으로 등록
        self._load_modules('modules.main.controllers', 'Controller')
        self._load_modules('modules.process_monitor.controllers', 'Controller')
        self._load_modules('modules.network_monitor.controllers', 'Controller')

    def _load_modules(self, package_path, class_suffix):
        # 주어진 패키지에서 모듈을 로드하고 특정 네이밍 규칙의 클래스들을 등록
        package = importlib.import_module(package_path)
        package_dir = package.__path__[0]

        for filename in os.listdir(package_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
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
