# main/main.py

import sys
import PySide6.QtCore
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from subwindows import homepage, newgameconfig, chessboard


class MainWindow(QMainWindow):
    def __init__(self, application: QApplication):
        super().__init__()
        print(f'Initialised Main Window, {self}')

        self.application = application
        self.stackedwidget = QStackedWidget()
        self.windowstack: list = []

        self.setCentralWidget(self.stackedwidget)
        self.instantiateSubwindows()
        self.setCurrentSubwindow(2)

    # Instantiate all sub windows of application
    def instantiateSubwindows(self) -> None:
        self.subwindow_instances = [
            homepage.SubWindow(self), newgameconfig.SubWindow(self), chessboard.SubWindow(self)
        ]

        for instance in self.subwindow_instances:
            self.stackedwidget.addWidget(instance)

    # Set current displayed sub window to specified index
    def setCurrentSubwindow(self, index: int) -> None:
        self.windowstack.append(self.stackedwidget.currentIndex())
        self.stackedwidget.currentWidget().closeWindows()
        self.stackedwidget.setCurrentIndex(index)
        self.stackedwidget.currentWidget().refresh()
        print(f'Subwindow change request, {self.stackedwidget.currentWidget()}')

    # Display previously opened sub window and remove
    # latest index from the stack
    def previousSubwindow(self) -> None:
        self.stackedwidget.currentWidget().closeWindows()
        self.stackedwidget.setCurrentIndex(self.windowstack[-1])
        self.stackedwidget.currentWidget().refresh()
        self.windowstack.pop()
        print(f'Subwindow change request, {self.stackedwidget.currentWidget()}')

    # Public method to close application
    def quitApplication(self) -> None:
        self.application.quit()

# Handles top-level exceptions
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

# Program entry point
if __name__ == '__main__':
    sys.excepthook = except_hook
    print(f'Running PySide6 v{PySide6.__version__}')

    # Program loop
    app = QApplication(sys.argv)
    mainwindow = MainWindow(app)
    mainwindow.show()
    sys.exit(app.exec())