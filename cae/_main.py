import sys
import typing

from subwindows import _homepage, _game_configuration, _chessboard

import PySide6.QtCore
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtGui import QIcon


class MainWindow(QMainWindow):

    def __init__(self, application: QApplication):
        super().__init__()

        self.application = application
        self.setWindowIcon(QIcon('icon.png'))

        self.subwindow_stack = []

        self.subwindows = QStackedWidget()
        self.setCentralWidget(self.subwindows)
        self.instantiateSubwindows()
        self.setCurrentSubWindow(0)
        self.centreMainWindow()

    def instantiateSubwindows(self):
        self.subwindow_instances = [
            _homepage.SubWindow(self), _game_configuration.SubWindow(self), _chessboard.SubWindow(self)
        ]

        for instance in self.subwindow_instances:
            self.subwindows.addWidget(instance)

    def setCurrentSubWindow(self, index):
        self.subwindow_stack.append(self.subwindows.currentIndex())
        self.subwindows.setCurrentIndex(index)
        self.subwindows.currentWidget().initWindow()

    def goToPreviousSubWindow(self):
        previous_index = self.subwindow_stack[-1]
        self.subwindows.setCurrentIndex(previous_index)
        self.subwindow_stack.pop()

    def centreMainWindow(self):
        frame = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())

    def closeApplication(self):
        self.application.quit()


# Handles top-level exceptions
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    sys.excepthook = except_hook
    print(f'Running PySide6 v{PySide6.__version__}')

    app = QApplication(sys.argv)
    w = MainWindow(app)
    w.show()
    sys.exit(app.exec())