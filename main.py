from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from modules.main.main_view import MainWindow
from modules.main.main_controller import MainController  # 컨트롤러 추가
from core.app_module import AppModule
import sys


def main():
    app = QApplication(sys.argv)  # QApplication 생성

    window = MainWindow()

    app_module = AppModule()
    app_module.init_modules(main_window=window)

    controller = MainController(config={}, view=window, app_module=app_module)
    window.controller = controller

    window.set_app_module(app_module)
    window.setWindowTitle("Isegye Viewer")
    window.setWindowIcon(QIcon("resources/images/favicon.png"))
    window.center()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
