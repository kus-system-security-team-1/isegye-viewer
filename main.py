from PyQt5.QtWidgets import QApplication, QMainWindow
import sys


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
