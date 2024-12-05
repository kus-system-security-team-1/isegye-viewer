from modules.main.main_service import MainService
from modules.main.main_view import PrevHistoryWindow, AlertWindow
from PyQt5.QtCore import Qt


class MainController:
    def __init__(self, config, view=None, app_module=None):
        self.view = view
        self.config = config
        self.app_module = app_module
        self.service = MainService(config)

        self.history_controller = self.app_module.get_controller(
            'HistoryController'
        )
        self.pe_controller = self.app_module.get_controller('PEController')
        self.process_controller = self.app_module.get_controller(
            'ProcesssController'
        )

    def switch_page(self, index):  # 상위 메뉴 페이지 전환
        page = {
            0: "프로세스 정보",
            1: "히스토리 추적",
            2: "네트워크 모니터링",
            3: "이전 분석 결과",
            4: "도움말",
        }
        if self.view:
            page_title = page.get(index, " ")
            self.view.page_title.setText(page_title)
            if index == 0:
                self.view.process_stackedWidget.setCurrentIndex(0)
            elif index == 1:
                self.view.history_stackedWidget.setCurrentIndex(0)
            elif index == 2:
                self.view.network_stackedWidget.setCurrentIndex(0)
            elif index == 3:
                self.view.btn_past.setVisible(False)

            self.view.page_stackedWidget.setCurrentIndex(index)

    def switch_prev_page(self, index):
        if self.view:
            self.view.prev_stackedWidget.setCurrentIndex(index)

    def prev_page_change_title(self, index):
        page = {
            0: "프로세스 정보",
            1: "히스토리 추적",
            2: "네트워크 모니터링",
            3: " ",
        }
        if self.view:
            if index == 3:
                self.view.prev_stackedWidget.setCurrentIndex(1)
            else:
                self.view.prev_stackedWidget.setCurrentIndex(0)
                self.view.btn_past.setVisible(True)
            page_title = page.get(index, " ")
            self.view.prev_page_title.setText(page_title)

    def analyze_process_info(self):
        self.view.process_stackedWidget.setCurrentIndex(1)

    def trace_history(self):
        self.view.history_stackedWidget.setCurrentIndex(1)

    def network_monitoring(self):
        self.view.network_stackedWidget.setCurrentIndex(1)

    def show_past_history(self):
        current_page = self.view.prev_page_title.text()
        if self.view.prevHistory_popup is None:
            self.view.prevHistory_popup = PrevHistoryWindow(parent=self.view)
            self.view.prevHistory_popup.setWindowModality(Qt.ApplicationModal)

        if current_page == "프로세스 정보":
            self.view.prevHistory_popup.prevHistory_stackedWidget.setCurrentIndex(
                0
            )
        elif current_page == "히스토리 추적":
            self.view.prevHistory_popup.prevHistory_stackedWidget.setCurrentIndex(
                1
            )
        elif current_page == "네트워크 모니터링":
            self.view.prevHistory_popup.prevHistory_stackedWidget.setCurrentIndex(
                2
            )
        else:
            return

        self.view.prevHistory_popup.show()

    def show_alert(self):
        if self.view.alert_popup is None:
            self.view.alert_popup = AlertWindow(parent=self.view)
        self.view.alert_popup.exec()
        self.view.alert_popup = None

    def test(self):
        test = self.get_all_processes.show_network_packets()
        print(test)

    def reset_prevHistory_popup(self):
        self.view.prevHistory_popup = None
