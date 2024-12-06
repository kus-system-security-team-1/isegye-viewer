from modules.main.main_service import MainService
from modules.main.main_view import PrevHistoryWindow, AlertWindow
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt, QTimer


class MainController:
    def __init__(self, config, view=None, app_module=None):
        self.view = view
        self.config = config
        self.app_module = app_module
        self.service = MainService(config)

        self.history_controller = self.app_module.get_controller(
            "HistoryController"
        )
        self.pe_controller = self.app_module.get_controller("PEController")
        self.process_controller = self.app_module.get_controller(
            "ProcesssController"
        )

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_process_table)

        self.timer.timeout.connect(self.update_history_table)
        self.timer.timeout.connect(self.update_network_table)
        self.timer.start(2000)  # 1초마다 갱신

    def update_process_table(self):
        if self.process_controller:
            data = self.process_controller.get_all_processes()
            if self.view:
                self.view.update_process_table(data)

    def update_history_table(self):
        if self.process_controller:
            data = self.process_controller.get_all_history_processes()
            if self.view:
                self.view.update_history_table(data)

    def update_network_table(self):
        if self.process_controller:
            data = self.process_controller.show_network_packets()
            if self.view:
                self.view.update_network_table(data)

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

    def reset_selection_process(self):
        self.view.selected_process = None
        self.view.selected_process_pid = None
        self.view.selected_process_label.setText("")

    def analyze_process_info(self, pid=None):
        if not pid:
            print("Invalid PID")
            return

        process = self.view.selected_process.text()
        if not process:
            print("Process name is empty.")
            return

        self.view.selected_process_label.setText(f"(PID: {pid})\n{process}")
        self.view.process_stackedWidget.setCurrentIndex(1)

        detail_info = self.process_controller.get_detail_process_info(pid)

        if not detail_info or not isinstance(detail_info, list):
            print("Invalid detail_info data")
            return

        process_data = detail_info[0]

        self.view.basic_info_table.setRowCount(1)
        self.view.basic_info_table.setColumnCount(len(process_data))

        for col, key in enumerate(process_data.keys()):
            item = QTableWidgetItem(str(process_data[key]))
            self.view.basic_info_table.setItem(0, col, item)

        dll_list = self.process_controller.get_process_modules(int(pid))
        self.view.dll_table.setRowCount(len(dll_list))
        self.view.dll_table.setColumnCount(2)

        for index, dll_path in enumerate(dll_list, start=1):
            index_item = QTableWidgetItem(str(index))
            dll_item = QTableWidgetItem(dll_path)

            self.view.dll_table.setItem(index - 1, 0, index_item)
            self.view.dll_table.setItem(index - 1, 1, dll_item)

        self.view.dll_table.setColumnWidth(0, 30)
        self.view.dll_table.setColumnWidth(1, 870)

        entropy = self.pe_controller.calculate_entropy(process)
        style = ""
        if entropy >= 7.8:
            style = "color: red;"
        elif entropy >= 7.5 and entropy < 7.8:
            style = "color: yellow;"
        elif entropy >= 6.5 and entropy < 7.5:
            style = "color: green;"
        else:
            style = "color: grey;"

        if entropy == -1:
            entropy = "예외 처리"

        self.view.entropy_value.setStyleSheet(style)
        self.view.entropy_value.setText(str(entropy))

    def trace_history(self, pid=None):
        try:
            if not pid:
                print("Invalid PID")
                return

            self.view.history_stackedWidget.setCurrentIndex(1)

            process = self.process_controller.get_process_name(pid)
            if process == "":
                process = "-"
            else:
                process = process.rsplit('\\', 1)[-1]

            detail_info = (
                self.process_controller.get_detail_history_process_info(pid)
            )
            if not detail_info or len(detail_info) == 0:
                print("Error: detail_info is empty")
                return

            process_data = detail_info[0]
            if not isinstance(process_data, dict):
                print("Error: process_data is not a dictionary")
                return

            self.view.history_ss_log_table.setRowCount(1)
            self.view.history_ss_log_table.setColumnCount(len(process_data))

            for col, key in enumerate(process_data.keys()):
                item = QTableWidgetItem(str(process_data[key]))
                self.view.history_ss_log_table.setItem(0, col, item)

        except Exception as e:
            print(f"Exception 발생: {e}")

    def network_monitoring(self, pid=None):
        try:
            if not pid:
                print("Invalid PID")
                return
            packet_info = []
            self.view.network_stackedWidget.setCurrentIndex(1)
            network_packets = (
                self.process_controller.show_all_network_packets()
            )

            selected_packet = [
                entry for entry in network_packets if entry['pid'] == pid
            ]
            if selected_packet:
                packet = selected_packet[0]
                time = "-"
                local_add = packet['local_address']
                remote_add = packet['remote_address']
                protocol = packet['protocol']
                status = packet['status']
                packet_size = "-"

                packet_info.append(
                    {
                        "time": time,
                        "local_add": local_add,
                        "remote_add": remote_add,
                        "protocol": protocol,
                        "status": status,
                        "packet_size": packet_size,
                    }
                )
                self.view.network_log_table.setRowCount(1)
                self.view.network_log_table.setColumnCount(6)

                for col, (key, value) in enumerate(packet_info[0].items()):
                    item = QTableWidgetItem(str(value))
                    self.view.network_log_table.setItem(0, col, item)

        except Exception as e:
            print(f"Network_monitoring : {e}")

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

    def reset_prevHistory_popup(self):
        self.view.prevHistory_popup = None
