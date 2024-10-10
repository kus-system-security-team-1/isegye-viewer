from PyQt5.QtWidgets import QApplication
from modules.main.main_view import MainWindow
from core.app_module import AppModule
import sys


def main():
    app = QApplication(sys.argv)
    app_module = AppModule()
    app_module.init_modules()

    window = MainWindow()
    window.set_app_module(app_module)

    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
