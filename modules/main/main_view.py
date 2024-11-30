from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QDesktopWidget, QDialog
from PyQt5.QtCore import Qt
import resources.resources_rc  # noqa


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/main_window.ui", self)
        self.controller = None
        self.app_module = None

        self.prevHistory_popup = None  # PrevHistoryWindow 참조
        self.alert_popup = None  # AlertWindow 참조

        self.page_stackedWidget.setCurrentIndex(0)
        self.process_stackedWidget.setCurrentIndex(0)
        self.history_stackedWidget.setCurrentIndex(0)
        self.network_stackedWidget.setCurrentIndex(0)
        self.basic_info_table.horizontalHeader().show()
        self.dll_table.horizontalHeader().show()
        self.pe_info_table.verticalHeader().show()
        self.filtering_table.horizontalHeader().show()
        self.history_table.horizontalHeader().show()
        self.history_ss_log_table.horizontalHeader().show()
        self.history_registry_table.horizontalHeader().show()
        self.network_table.horizontalHeader().show()
        self.network_log_table.horizontalHeader().show()
        self.prev_table.horizontalHeader().show()
        self.basic_info_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft
        )
        self.dll_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.pe_info_table.verticalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.filtering_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft
        )
        self.history_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.history_ss_log_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft
        )
        self.history_registry_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft
        )
        self.network_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.network_log_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft
        )
        self.prev_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.prev_menu_group.setVisible(False)
        self.btn_past.setVisible(False)
        self.btn_process_menu.setChecked(True)
        self.init_ui()
        self.center()

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

        self.btn_past.clicked.connect(self.controller.show_past_history)

        self.btn_test.clicked.connect(self.controller.show_alert)


class PrevHistoryWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/prevHistory_window.ui", self)
        self.prevHistory_registry_table.horizontalHeader().show()
        self.prevHistory_ss_log_table.horizontalHeader().show()
        self.prev_process_basic_info_table.horizontalHeader().show()
        self.prev_process_entropy_table.horizontalHeader().show()
        self.prevHistory_network_table.horizontalHeader().show()
        self.prevHistory_network_info_table.horizontalHeader().show()
        self.prevHistory_registry_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft
        )
        self.prevHistory_ss_log_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft
        )
        self.prev_process_basic_info_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft
        )
        self.prev_process_entropy_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft
        )
        self.prevHistory_network_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft
        )
        self.prevHistory_network_info_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft
        )
        self.controller = None
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.prevHistory_stackedWidget.setCurrentIndex(0)
        self.init_ui()
        self.move(170, 137)

    def init_ui(self):
        self.btn_ok.clicked.connect(self.close)

    def closeEvent(self, event):
        if self.parent():
            self.parent().prevHistory_popup = None
        event.accept()


class AlertWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/alert_window.ui", self)
        self.controller = None
        self.alert_stackedWidget.setCurrentIndex(0)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.init_ui()

    def init_ui(self):
        self.btn_ok_1.clicked.connect(self.accept)
        self.btn_ok_2.clicked.connect(self.accept)
