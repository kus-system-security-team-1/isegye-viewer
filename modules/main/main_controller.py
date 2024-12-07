from modules.main.main_service import MainService
from modules.main.main_view import PrevHistoryWindow, AlertWindow
from PyQt5.QtWidgets import QTableWidgetItem, QLabel
from PyQt5.QtCore import Qt, QTimer
from lib.isegye_viewer_core import DetectEntropyType


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
        self.timer.timeout.connect(self.update_tables)  # 하나의 슬롯에 연결
        self.timer.start(1000)  # 1초마다 갱신

    def update_tables(self):
        if self.view.insert_pe_stackedWidget.currentIndex() == 2:
            self.update_process_table()

        if self.view.history_toggle.isChecked():
            self.view.history_table.setVisible(True)
            self.view.history_process_search_bar.setEnabled(True)
            self.view.btn_history_analyze.setEnabled(True)
            self.view.history_process_search_bar.setEnabled(True)
            self.update_history_table()
        else:
            self.view.history_process_search_bar.setEnabled(False)
            self.view.btn_history_analyze.setEnabled(False)
            self.view.history_table.setVisible(False)
            self.view.history_process_search_bar.setEnabled(False)

        if self.view.network_toggle.isChecked():
            self.view.network_table.setVisible(True)
            self.view.network_process_search_bar.setEnabled(True)
            self.view.btn_network_analyze.setEnabled(True)
            self.view.network_process_search_bar.setEnabled(True)
            self.update_network_table()
        else:
            self.view.network_process_search_bar.setEnabled(False)
            self.view.btn_network_analyze.setEnabled(False)
            self.view.network_process_search_bar.setEnabled(False)
            self.view.network_table.setVisible(False)

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
        try:
            if not pid:
                print("Invalid PID")
                return

            process = self.view.selected_process.text()
            if not process:
                print("Process name is empty.")
                return

            self.view.selected_process_label.setText(
                f"(PID: {pid})\n{process}"
            )
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

            self.show_detail_dll(pid)

            process_name = self.process_controller.get_process_name(int(pid))
            entropy, level_entropy = self.pe_controller.detect_entropy(
                process_name
            )
            style = ""

            if level_entropy == DetectEntropyType.HIGH:
                style = "color: red;"
            elif level_entropy == DetectEntropyType.MIDDLE:
                style = "color: orange;"
            elif level_entropy == DetectEntropyType.LOW:
                style = "color: green;"
            else:
                style = "color: grey;"

            self.view.entropy_value.setStyleSheet(style)
            print(
                f"level : {level_entropy}, type : {type(level_entropy)}, style : {style}"
            )
            self.view.entropy_value.setText(str(entropy))

        except Exception as e:
            print(f"Error : {e}")

    def show_detail_dll(self, pid=None):

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

            self.history_controller.log_process_times_to_file(
                int(pid), process
            )
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

    def search_dll(self):
        search_text = self.view.dll_search_bar.text().strip()
        if not search_text:
            pid = self.view.selected_process_pid
            self.show_detail_dll(pid)
            return

        row_count = self.view.dll_table.rowCount()
        matching_rows = []

        for row in range(row_count):
            dll_item = self.view.dll_table.item(
                row, 1
            )  # DLL 경로가 있는 열 가져오기
            if dll_item and search_text.lower() in dll_item.text().lower():
                matching_rows.append((row, dll_item.text()))

        # 검색 결과를 테이블에 표시
        if matching_rows:
            self.view.dll_table.setRowCount(len(matching_rows))
            for index, (original_row, dll_path) in enumerate(matching_rows):
                index_item = QTableWidgetItem(str(index + 1))
                dll_item = QTableWidgetItem(dll_path)

                self.view.dll_table.setItem(index, 0, index_item)
                self.view.dll_table.setItem(index, 1, dll_item)
        else:
            # 검색 결과가 없으면 "존재하지 않습니다" 표시
            self.view.dll_table.setRowCount(1)
            self.view.dll_table.setColumnCount(1)
            self.view.dll_table.setItem(
                0, 0, QTableWidgetItem("존재하지 않습니다")
            )

        # 테이블 레이아웃 조정
        self.view.dll_table.setColumnWidth(0, 30)
        self.view.dll_table.setColumnWidth(1, 870)

    def search_process(self):
        search_text = self.view.process_search_bar.text().strip()
        if not search_text:
            self.view.insert_pe_stackedWidget.setCurrentIndex(2)

        # 모델 가져오기
        model = self.view.show_processes_table.model()
        if model is None:
            print("No model set for the table.")
            return

        matching_rows = []
        for row in range(model.rowCount()):
            index = model.index(row, 1)  # 프로세스 이름이 있는 열 (1번 열)
            process_name = model.data(index, Qt.DisplayRole)

            if process_name and search_text.lower() in process_name.lower():
                pid_index = model.index(row, 0)  # PID가 있는 열 (0번 열)
                pid = model.data(pid_index, Qt.DisplayRole)
                matching_rows.append((pid, process_name))

        # 검색 결과를 show_same_name_process_table에 표시
        if matching_rows:
            self.view.insert_pe_stackedWidget.setCurrentIndex(3)
            self.view.show_same_name_process_table.setRowCount(
                len(matching_rows)
            )
            self.view.show_same_name_process_table.setColumnCount(
                2
            )  # PID, 프로세스 이름
            self.view.show_same_name_process_table.doubleClicked.connect(
                self.on_table_double_click
            )

            for index, (pid, process_name) in enumerate(matching_rows):
                pid_item = QTableWidgetItem(str(pid))
                name_item = QTableWidgetItem(process_name)

                self.view.show_same_name_process_table.setItem(
                    index, 0, pid_item
                )
                self.view.show_same_name_process_table.setItem(
                    index, 1, name_item
                )
        else:
            self.view.insert_pe_stackedWidget.setCurrentIndex(3)
            self.view.show_same_name_process_table.setRowCount(1)
            self.view.show_same_name_process_table.setColumnCount(1)
            self.view.show_same_name_process_table.setItem(
                0, 0, QTableWidgetItem("존재하지 않습니다")
            )

        self.view.show_same_name_process_table.setColumnWidth(
            0, 200
        )  # PID 열 너비
        self.view.show_same_name_process_table.setColumnWidth(
            1, 470
        )  # 프로세스 이름 열 너비

    def on_table_double_click(self, index):
        try:
            if not index.isValid():
                return

            # 더블 클릭된 행과 열의 데이터 가져오기
            row = index.row()
            pid_item = self.view.show_same_name_process_table.item(
                row, 0
            )  # PID (첫 번째 열)
            name_item = self.view.show_same_name_process_table.item(
                row, 1
            )  # 프로세스 이름 (두 번째 열)

            if pid_item and name_item:
                pid = pid_item.text()
                process_name = name_item.text()
                self.view.selected_process_pid = pid
                self.view.selected_process = self.view.findChild(
                    QLabel, "selected_process"
                )
                self.view.selected_process.setText(process_name)
                self.view.insert_pe_stackedWidget.setCurrentIndex(1)
        except Exception as e:
            print(f"Error: {e}")

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
