from modules.main.main_service import MainService


class MainController:
    def __init__(self, config, view=None):
        self.view = view
        self.config = config
        self.service = MainService(config)

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
            page_title = page.get(index, " ")
            self.view.prev_page_title.setText(page_title)

    def analyze_process_info(self):
        self.view.process_stackedWidget.setCurrentIndex(1)

    def trace_history(self):
        self.view.history_stackedWidget.setCurrentIndex(1)

    def network_monitoring(self):
        self.view.network_stackedWidget.setCurrentIndex(1)
