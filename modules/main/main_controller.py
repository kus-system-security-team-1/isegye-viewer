from modules.main.main_service import MainService
from modules.main.main_view import PrevHistoryWindow, AlertWindow
from PyQt5.QtWidgets import QTableWidgetItem, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime
import json, re
from lib.isegye_viewer_core import DetectEntropyType


class MainController:
    def __init__(
        self,
        config,
        view=None,
        app_module=None,
        filtering_table_file="filtering_table.json",
    ):
        self.view = view
        self.config = config
        self.app_module = app_module
        self.service = MainService(config)

        self.filtering_table_file = filtering_table_file
        self.filtering_data = []
        self.load_filtering_table()
        self.update_filtering_table()

        self.history_controller = self.app_module.get_controller(
            "HistoryController"
        )
        self.pe_controller = self.app_module.get_controller("PEController")
        self.process_controller = self.app_module.get_controller(
            "ProcesssController"
        )

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_tables)
        self.timer.start(1000)

        self.network_timer = QTimer()
        self.network_timer.timeout.connect(self.refresh_network_data)
        self.network_current_pid = None

        self.view.network_stackedWidget.currentChanged.connect(
            self.check_network_page
        )
        self.view.network_toggle.toggled.connect(
            self.on_network_toggle_changed
        )

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
            self.view.entropy_value.setText(str(entropy))

            if self.view.alert_popup is None:
                self.view.alert_popup = AlertWindow(parent=self.view)
            self.view.alert_popup.set_alert_message(level_entropy, process)
            self.view.alert_popup.exec()
            self.view.alert_popup = None

        except Exception as e:
            print(f"Error : {e}")

    def show_detail_dll(self, pid=None):
        dll_list = self.process_controller.get_process_modules(int(pid))
        self.view.dll_table.setRowCount(len(dll_list))
        self.view.dll_table.setColumnCount(2)

        # 필터링 목록 (이름만 추출)
        filtering_dlls = [item["name"].lower() for item in self.filtering_data]

        for index, dll_path in enumerate(dll_list, start=1):
            index_item = QTableWidgetItem(str(index))
            dll_item = QTableWidgetItem(dll_path)

            dll_name = dll_path.split("\\")[-1].lower()
            if dll_name in filtering_dlls:
                index_item.setForeground(Qt.red)
                dll_item.setForeground(Qt.red)

                for row, item in enumerate(self.filtering_data):
                    if item["name"].lower() == dll_name:
                        item["status"] = "detected"
                        self.view.filtering_table.item(row, 1).setText(
                            "detected"
                        )
                        self.view.filtering_table.item(row, 1).setForeground(
                            Qt.green
                        )
                        break

            self.view.dll_table.setItem(index - 1, 0, index_item)
            self.view.dll_table.setItem(index - 1, 1, dll_item)

        self.view.dll_table.setColumnWidth(0, 30)
        self.view.dll_table.setColumnWidth(1, 870)
        self.save_filtering_table()

    def load_filtering_table(self):
        try:
            with open(
                self.filtering_table_file, "r", encoding="utf-8"
            ) as file:
                self.filtering_data = json.load(file)
        except FileNotFoundError:
            self.filtering_data = []
        except json.JSONDecodeError:
            print("JSON 파일을 읽을 수 없습니다.")
            self.filtering_data = []

    def save_filtering_table(self):
        try:
            with open(
                self.filtering_table_file, "w", encoding="utf-8"
            ) as file:
                json.dump(
                    self.filtering_data, file, ensure_ascii=False, indent=4
                )
        except Exception as e:
            print(f"Error: 필터링 테이블 저장 중 문제가 발생했습니다. {e}")

    def add_to_filtering_table(self):
        name = self.view.filtering_search_bar.text().strip()

        dll_pattern = r"^[a-zA-Z0-9_\-]+\.dll$"
        if not re.match(dll_pattern, name, re.IGNORECASE):
            print("Error: 잘못된 형식의 DLL 이름입니다. 예: test.dll")
            self.view.filtering_search_bar.clear()
            return

        if not name or any(
            item["name"].lower() == name.lower()
            for item in self.filtering_data
        ):
            return

        new_entry = {"name": name, "status": "undetected"}
        self.filtering_data.append(new_entry)
        self.save_filtering_table()
        self.update_filtering_table()

        self.view.filtering_search_bar.clear()

    def update_filtering_table(self):
        """테이블 UI를 업데이트 및 스타일 유지"""
        table = self.view.filtering_table
        table.setRowCount(len(self.filtering_data))

        for row, item in enumerate(self.filtering_data):
            name = item.get("name", "")
            status = item.get("status", "undetected")

            # 이름 설정
            name_item = QTableWidgetItem(name)
            table.setItem(row, 0, name_item)

            # 감지 여부 설정
            status_item = QTableWidgetItem(status)
            if status == "detected":
                status_item.setForeground(Qt.green)  # 연두색
            else:
                status_item.setForeground(Qt.red)  # 빨간색
            table.setItem(row, 1, status_item)

            # 삭제 버튼 추가
            delete_button = QPushButton("삭제", self.view)
            delete_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #ff4d4d;  /* 붉은 배경 */
                    color: white;              /* 흰색 텍스트 */
                    border: none;              /* 테두리 없음 */
                    border-radius: 5px;        /* 둥근 모서리 */
                    padding: 5px 10px;         /* 내부 여백 */
                }
                QPushButton:hover {
                    background-color: #ff1a1a; /* 호버 시 더 어두운 빨강 */
                }
                QPushButton:pressed {
                    background-color: #cc0000; /* 클릭 시 더 어두운 빨강 */
                }
                """
            )
            delete_button.clicked.connect(
                lambda _, r=row: self.remove_from_filtering_table(r)
            )
            table.setCellWidget(row, 2, delete_button)

    def remove_from_filtering_table(self, row):
        if 0 <= row < len(self.filtering_data):
            del self.filtering_data[row]
            self.save_filtering_table()
            self.update_filtering_table()

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
                print("First Invalid PID")
                return
            if self.view.network_toggle.isChecked():
                self.network_current_pid = int(pid)
                self.view.network_stackedWidget.setCurrentIndex(1)

                self.view.network_log_table.setRowCount(0)
                self.refresh_network_data()
                self.network_timer.start(1000)
            else:
                print(
                    "Network toggle is not checked. Monitoring cannot start."
                )

        except Exception as e:
            print(f"Network_monitoring : {e}")

    def refresh_network_data(self):
        try:
            if not self.view.network_toggle.isChecked():
                self.stop_network_monitoring()
                return

            if not self.network_current_pid:
                print("Second Invalid PID")
                return
            network_packets = (
                self.process_controller.show_all_network_packets()
            )

            selected_packet = [
                entry
                for entry in network_packets
                if entry['pid'] == self.network_current_pid
            ]
            if selected_packet:
                packet = selected_packet[0]
                current_time = datetime.now().strftime("%H:%M:%S")
                packet_info = {
                    "time": current_time,
                    "local_add": packet['local_address'],
                    "remote_add": packet['remote_address'],
                    "protocol": packet['protocol'],
                    "status": packet['status'],
                    "packet_size": "-",
                }
                current_row_count = self.view.network_log_table.rowCount()
                self.view.network_log_table.insertRow(current_row_count)

                for col, (key, value) in enumerate(packet_info.items()):
                    item = QTableWidgetItem(str(value))
                    self.view.network_log_table.setItem(
                        current_row_count, col, item
                    )

        except Exception as e:
            print(f"network table error : {e}")

    def stop_network_monitoring(self):
        self.network_timer.stop()
        self.current_pid = None

    def check_network_page(self, index):
        if index == 1 and self.view.network_toggle.isChecked():
            if self.network_current_pid:
                self.network_timer.start(1000)
            else:
                self.stop_network_monitoring()

    def on_network_toggle_changed(self, checked):
        if checked:
            if (
                self.view.network_stackedWidget.currentIndex() == 1
                and self.network_current_pid
            ):
                self.network_timer.start(1000)
            else:
                self.stop_network_monitoring()

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

        model = self.view.show_processes_table.model()
        if model is None:
            print("No model set for the table.")
            return

        matching_rows = []
        for row in range(model.rowCount()):
            index = model.index(row, 1)
            process_name = model.data(index, Qt.DisplayRole)

            if process_name and search_text.lower() in process_name.lower():
                pid_index = model.index(row, 0)
                pid = model.data(pid_index, Qt.DisplayRole)
                matching_rows.append((pid, process_name))

        if matching_rows:
            self.view.insert_pe_stackedWidget.setCurrentIndex(3)
            self.view.show_same_name_process_table.setRowCount(
                len(matching_rows)
            )
            self.view.show_same_name_process_table.setColumnCount(2)
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

        self.view.show_same_name_process_table.setColumnWidth(0, 200)
        self.view.show_same_name_process_table.setColumnWidth(1, 470)

    def on_table_double_click(self, index):
        try:
            if not index.isValid():
                return

            row = index.row()
            pid_item = self.view.show_same_name_process_table.item(row, 0)
            name_item = self.view.show_same_name_process_table.item(row, 1)

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
