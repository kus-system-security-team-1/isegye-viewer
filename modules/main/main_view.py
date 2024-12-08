from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QDesktopWidget,
    QDialog,
    QTableView,
    QHeaderView,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QFrame,
)
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from common.base_window import BaseWindow
from lib.isegye_viewer_core import DetectEntropyType
import resources.resources_rc  # noqa


class MainWindow(QMainWindow, BaseWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        BaseWindow.__init__(self, "ui/main_window.ui")

        self.controller = None
        self.app_module = None

        self.prevHistory_popup = None  # PrevHistoryWindow 참조
        self.alert_popup = None  # AlertWindow 참조

        self.history_on_off = None
        self.network_on_off = None

        self.page_stackedWidget.setCurrentIndex(0)
        self.process_stackedWidget.setCurrentIndex(0)
        self.history_stackedWidget.setCurrentIndex(0)
        self.network_stackedWidget.setCurrentIndex(0)
        self.insert_pe_stackedWidget.setCurrentIndex(0)
        self.basic_info_table.horizontalHeader().show()
        self.dll_table.horizontalHeader().show()
        self.filtering_table.horizontalHeader().show()
        self.history_table.horizontalHeader().show()
        self.history_ss_log_table.horizontalHeader().show()
        self.history_registry_table.horizontalHeader().show()
        self.network_table.horizontalHeader().show()
        self.network_log_table.horizontalHeader().show()
        self.prev_table.horizontalHeader().show()
        self.show_same_name_process_table.horizontalHeader().show()
        self.basic_info_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft
        )
        self.dll_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
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
        self.show_processes_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft
        )
        self.prev_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.show_same_name_process_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignLeft
        )
        headers = ["PID", "프로세스 이름"]
        self.show_same_name_process_table.setHorizontalHeaderLabels(headers)
        self.basic_info_table.setWordWrap(True)
        self.selected_process_label.setWordWrap(True)
        self.dll_table.setWordWrap(True)

        self.prev_menu_group.setVisible(False)
        self.btn_past.setVisible(False)
        self.btn_process_menu.setChecked(True)
        self.center()

        # 표 관련
        self.process_table_elements()
        self.history_table_elements()
        self.network_table_elements()
        self.selected_process = None
        self.selected_process_pid = None

        self.setup_line_edit_event()

    def center(self):  # 모니터 정중앙에 화면 띄우기
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui(self):
        super().init_ui("MainController")
        self.btn_process_menu.clicked.connect(
            lambda: (
                self.controller.switch_page(0),
                self.controller.reset_selection_process(),
                self.insert_pe_stackedWidget.setCurrentIndex(0),
                self.process_search_bar.clear(),
            )
        )
        self.btn_history_menu.clicked.connect(
            lambda: (
                self.controller.switch_page(1),
                self.controller.reset_selection_process(),
            )
        )
        self.btn_network_menu.clicked.connect(
            lambda: (
                self.controller.switch_page(2),
                self.network_tab.setCurrentIndex(0),
                self.controller.reset_selection_process(),
            )
        )
        self.btn_previous_menu.clicked.connect(
            lambda: (
                self.controller.switch_page(3),
                self.controller.switch_prev_page(1),
                self.controller.prev_page_change_title(3),
                self.controller.reset_selection_process(),
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
            lambda: self.controller.analyze_process_info(
                getattr(self, 'selected_process_pid', None)
            )
        )
        self.btn_history_analyze.clicked.connect(
            lambda: self.controller.trace_history(
                getattr(self, 'selected_process_pid', None)
            )
        )
        self.btn_network_analyze.clicked.connect(
            lambda: self.controller.network_monitoring(
                getattr(self, 'selected_process_pid', None)
            )
        )

        self.btn_past.clicked.connect(self.controller.show_past_history)
        self.btn_process_prev.clicked.connect(
            lambda: (
                self.controller.reset_selection_process,
                self.insert_pe_stackedWidget.setCurrentIndex(0),
            )
        )

        self.dll_search_bar.textChanged.connect(self.controller.search_dll)
        self.process_search_bar.textChanged.connect(
            self.controller.search_process
        )
        self.filtering_search_bar.returnPressed.connect(
            self.controller.add_to_filtering_table
        )

    # 표 표시 메소드

    def process_table_elements(self):
        self.show_processes_table = self.findChild(
            QTableView, 'show_processes_table'
        )
        self.process_model = ProcessTableModel()
        self.show_processes_table.setModel(self.process_model)

        self.show_processes_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive
        )  # 열 크기 조정 가능
        self.show_processes_table.setColumnWidth(
            0, 200
        )  # PID 열 너비 (픽셀 단위)
        self.show_processes_table.setColumnWidth(
            1, 470
        )  # 프로세스 이름 열 너비 (픽셀 단위)
        self.show_processes_table.doubleClicked.connect(
            self.on_row_double_click
        )

    def history_table_elements(self):
        self.history_table = self.findChild(QTableView, 'history_table')

        self.history_model = HistoryTableModel()
        self.history_table.setModel(self.history_model)

        self.history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive
        )

        self.history_table.setColumnWidth(0, 550)  # 프로세스 이름 열 너비
        self.history_table.setColumnWidth(1, 550)  # 사용자 이름 열 너비

        self.history_table.doubleClicked.connect(
            self.on_history_row_double_click
        )

    def network_table_elements(self):
        self.network_table = self.findChild(QTableView, 'network_table')

        self.network_model = NetworkTableModel()
        self.network_table.setModel(self.network_model)

        self.network_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive
        )

        self.network_table.setColumnWidth(0, 500)  # 프로세스 이름 열 너비
        self.network_table.setColumnWidth(1, 500)  # 사용자 이름 열 너비

        self.network_table.doubleClicked.connect(
            self.on_network_row_double_click
        )

    def update_process_table(self, data):
        self.process_model.update_data(data)

    def update_history_table(self, data):
        self.history_model.update_data(data)

    def update_network_table(self, data):
        self.network_model.update_data(data)

    def setup_line_edit_event(self):
        self.process_search_bar = self.findChild(
            QLineEdit, 'process_search_bar'
        )
        if self.process_search_bar:
            self.process_search_bar.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.process_search_bar:
            if event.type() == QtCore.QEvent.FocusIn:
                self.insert_pe_stackedWidget.setCurrentIndex(2)
                return True
            elif event.type() == QtCore.QEvent.MouseButtonPress:
                self.insert_pe_stackedWidget.setCurrentIndex(2)
                return True
        return super(MainWindow, self).eventFilter(obj, event)

    def on_row_double_click(self, index):
        if index.isValid():
            row = index.row()
            index = self.process_model.index(row, 0)
            name_index = self.process_model.index(row, 1)
            process_name = self.process_model.data(name_index, Qt.DisplayRole)
            process_pid = self.process_model.data(index, Qt.DisplayRole)

            self.selected_process = self.findChild(QLabel, "selected_process")
            self.selected_process.setText(process_name)
            self.selected_process_pid = process_pid

            self.insert_pe_stackedWidget.setCurrentIndex(1)

    def on_history_row_double_click(self, index):
        try:
            if not index.isValid():
                print("Invalid index")
                return

            row = index.row()
            print(f"Selected row: {row}")
            self.selected_process_pid = self.history_model.get_pid(row)
            if self.selected_process_pid is None:
                print(f"Error: PID를 찾을 수 없습니다. (row: {row})")
                return

            process_name_index = self.history_model.index(row, 0)
            process_name = self.history_model.data(
                process_name_index, Qt.DisplayRole
            )

            self.selected_process_label = self.findChild(
                QLabel, "selected_process_label"
            )

            self.selected_process_label.setText(
                f"(PID: {self.selected_process_pid})\n{process_name}"
            )
        except Exception as e:
            print(f"Exception 발생: {e}")

    def on_network_row_double_click(self, index):
        try:
            if not index.isValid():
                print("Invalid index")
                return

            row = index.row()
            self.selected_process_pid = self.network_model.get_pid(row)
            process_name_index = self.network_model.index(row, 0)
            process_name = self.network_model.data(
                process_name_index, Qt.DisplayRole
            )

            self.selected_process_label = self.findChild(
                QLabel, "selected_process_label"
            )
            self.selected_process_label.setText(
                f"(PID: {self.selected_process_pid})\n{process_name}"
            )
        except Exception as e:
            print(f"Exception 발생: {e}")

    def update_filtering_table(self, data):
        self.filtering_table.setRowCount(len(data))
        for row, item in enumerate(data):
            dll_name = item.get("dll_name", "")
            detection_status = item.get("detection_status", "정상")

            # DLL 이름
            self.filtering_table.setItem(row, 0, QTableWidgetItem(dll_name))

            # 감지 여부
            self.filtering_table.setItem(
                row, 1, QTableWidgetItem(detection_status)
            )

            # 삭제 버튼
            delete_button = QPushButton("삭제", self)
            delete_button.clicked.connect(
                lambda _, r=row: self.controller.remove_from_filtering_dll_table(
                    r
                )
            )
            self.filtering_table.setCellWidget(row, 2, delete_button)


class PrevHistoryWindow(QWidget, BaseWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        BaseWindow.__init__(self, "ui/prevHistory_window.ui")
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
        self.center()
        self.init_ui()

    def center(self):  # 모니터 정중앙에 화면 띄우기
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui(self):
        self.btn_ok.clicked.connect(self.close)

    def closeEvent(self, event):
        if self.parent():
            self.parent().prevHistory_popup = None
        event.accept()


class AlertWindow(QDialog, BaseWindow):
    def __init__(self, parent=None):
        QDialog.__init__(self)
        BaseWindow.__init__(self, "ui/alert_window.ui")
        self.controller = None
        self.alert_stackedWidget.setCurrentIndex(1)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.center()
        self.init_ui()

    def center(self):  # 모니터 정중앙에 화면 띄우기
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui(self):
        self.btn_ok_1.clicked.connect(self.accept)
        self.btn_ok_2.clicked.connect(self.accept)

    def set_alert_message(self, level_entropy, process_name):
        label_style = ""
        process_name_label = self.findChild(QLabel, "process_name_label_2")
        frame_label = self.findChild(QFrame, "suspect_alert_frame")
        text_label = self.findChild(QLabel, "suspect_level")

        if level_entropy == DetectEntropyType.HIGH:
            label_style = "color: red;"
            text_label.setText("높음")
            frame_label.setStyleSheet(
                """
            #suspect_alert_frame {
                background-color: #EEE6DD;
                border: 5px solid #EE8181;
                border-radius: 25px;
            }
            """
            )
        elif level_entropy == DetectEntropyType.MIDDLE:
            label_style = "color: orange;"
            text_label.setText("중간")
            frame_label.setStyleSheet(
                """
            #suspect_alert_frame {
                background-color: #EEE6DD;
                border: 5px solid #FE7614;
                border-radius: 25px;
            }
            """
            )
        elif level_entropy == DetectEntropyType.LOW:
            label_style = "color: green;"
            text_label.setText("정상")
            frame_label.setStyleSheet(
                """
            #suspect_alert_frame {
                background-color: #EEE6DD;
                border: 5px solid #AAD298;
                border-radius: 25px;
            }
            """
            )
        else:
            label_style = "color: grey;"
            text_label.setText("예외 처리")
            frame_label.setStyleSheet(
                """
            #suspect_alert_frame {
                background-color: #EEE6DD;
                border: 5px solid #AAD298;
                border-radius: 25px;
            }
            """
            )
        process_name_label.setText(process_name)
        text_label.setStyleSheet(label_style)


# 실행 중인 프로세스 표시 클래스
class ProcessTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super(ProcessTableModel, self).__init__()
        self._data = data or []
        self._headers = ['PID', '프로세스 이름']

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            process = self._data[index.row()]
            column = index.column()
            if column == 0:
                return str(process.get('pid', ''))
            elif column == 1:
                return process.get('name', '')
        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section]
        return None

    def update_data(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()


class HistoryTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super(HistoryTableModel, self).__init__()
        self._data = data or []
        self._headers = [
            '프로세스',
            '사용자 이름',
        ]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            process = self._data[index.row()]
            column = index.column()
            if column == 0:
                return str(process.get('name', ''))  # '프로세스' 열
            elif column == 1:
                return str(process.get('username', ''))  # 'CPU' 열
        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section]
        return None

    def get_pid(self, row):
        """특정 행의 PID를 반환 (표시하지 않는 데이터)"""
        if 0 <= row < len(self._data):
            return self._data[row].get('pid', None)
        return None

    def update_data(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()


class NetworkTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super(NetworkTableModel, self).__init__()
        self._data = data or []
        self._headers = [
            '프로세스',
            '사용자 이름',
        ]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            process = self._data[index.row()]
            column = index.column()
            if column == 0:
                return str(process.get('name', ''))
            elif column == 1:
                return str(process.get('username', ''))

        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section]
        return None

    def update_data(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

    def get_pid(self, row):
        """특정 행의 PID를 반환 (표시하지 않는 데이터)"""
        if 0 <= row < len(self._data):
            return self._data[row].get('pid', None)
        return None
