from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget
import resources.resources_rc  # noqa


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/main_window.ui", self)
        self.controller = None
        self.app_module = None
        self.page_stackedWidget.setCurrentIndex(0)
        self.process_stackedWidget.setCurrentIndex(0)
        self.history_stackedWidget.setCurrentIndex(0)
        self.network_stackedWidget.setCurrentIndex(0)
        self.basic_info_table.horizontalHeader().show()
        self.dll_table.horizontalHeader().show()
        self.pe_info_table.verticalHeader().show()
        self.filtering_table.horizontalHeader().show()
        self.history_table.horizontalHeader().show()
        self.history_start_stop_log_table.horizontalHeader().show()
        self.history_registry_table.horizontalHeader().show()
        self.network_table.horizontalHeader().show()
        self.network_log_table.horizontalHeader().show()
        self.prev_table.horizontalHeader().show()
        self.prev_menu_group.setVisible(False)
        self.btn_process_menu.setChecked(True)
        self.init_ui()

    def center(self):  # 모니터 정중앙에 화면 띄우기
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def set_app_module(self, app_module):
        self.app_module = app_module
        self.init_ui()

    def init_ui(self):
        if self.app_module:
            self.controller = self.app_module.get_controller("MainController")
        if not self.controller:
            return

        self.btn_process_menu.clicked.connect(
            lambda: self.controller.switch_page(0)
        )
        self.btn_history_menu.clicked.connect(
            lambda: self.controller.switch_page(1)
        )
        self.btn_network_menu.clicked.connect(
            lambda: (
                self.controller.switch_page(2),
                self.network_tab.setCurrentIndex(0),
            )
        )
        self.btn_previous_menu.clicked.connect(
            lambda: (
                self.controller.switch_page(3),
                self.controller.switch_prev_page(1),
                self.controller.prev_page_change_title(3),
            )
        )

        self.btn_help_menu.clicked.connect(
            lambda: (
                self.controller.switch_page(4),
                self.help_tab.setCurrentIndex(0),
            )
        )

        self.btn_prev_process_menu.clicked.connect(
            lambda: self.controller.prev_page_change_title(0)
        )
        self.btn_prev_history_menu.clicked.connect(
            lambda: self.controller.prev_page_change_title(1)
        )
        self.btn_prev_network_menu.clicked.connect(
            lambda: self.controller.prev_page_change_title(2)
        )
        self.btn_prev_process_2.clicked.connect(
            lambda: self.controller.prev_page_change_title(0)
        )
        self.btn_prev_history_2.clicked.connect(
            lambda: self.controller.prev_page_change_title(1)
        )
        self.btn_prev_network_2.clicked.connect(
            lambda: self.controller.prev_page_change_title(2)
        )

        self.btn_process_analyze.clicked.connect(
            self.controller.analyze_process_info
        )
        self.btn_history_analyze.clicked.connect(self.controller.trace_history)
        self.btn_network_analyze.clicked.connect(
            self.controller.network_monitoring
        )
