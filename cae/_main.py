import sys

from subwindows import _game_configuration, _chessboard, homepage

import PySide6.QtCore
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtGui import QIcon


# Main application window
class MainWindow(QMainWindow):
    
    def __init__(self, application):
        super().__init__()

        self.application = application
        self.setWindowIcon(QIcon('icon.png'))

        self.subwindow_stack = []

        # Initialise a stacked widget for navigating through sub windows
        self.subwindows = QStackedWidget()
        self.setCentralWidget(self.subwindows)
        self.initSubWindows()

        self.centerWindow()

        self.moveToWindow(0)

    # Instantiate sub window objects and add to stacked widget
    def initSubWindows(self):
        self.sub_instances = (
            homepage.SubWindow(self), _game_configuration.SubWindow(self),
            _chessboard.SubWindow(self)
        )

        for subwindow in self.sub_instances:
            self.subwindows.addWidget(subwindow)

    # Center window proportional to display dimensions
    def centerWindow(self):
        frame = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())

    # Function for moving to a previous sub window
    def previousWindow(self):
        self.subwindows.setCurrentIndex(self.subwindow_stack[-2])
        self.subwindow_stack.pop(-1)
        self.subwindows.currentWidget().initWindow()

    # Function for moving to a specific sub window
    def moveToWindow(self, desired_index):
        self.subwindows.setCurrentIndex(desired_index)
        self.subwindow_stack.append(desired_index)
        self.subwindows.currentWidget().initWindow()

    def closeApplication(self):
        self.application.quit()


# Handle exceptions
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# Program entry point
if __name__ == '__main__':
    sys.excepthook = except_hook
    print(f'Running PySide6 v{PySide6.__version__}') # debug log
    app = QApplication(sys.argv)
    w = MainWindow(app)
    w.show()
    sys.exit(app.exec())