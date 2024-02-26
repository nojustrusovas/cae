# main/main.py

import sys
import PySide6.QtCore
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from subwindows import homepage, newgameconfig, chessboard
from engine import ChessEngine
from logic import Board


class MainWindow(QMainWindow):
    def __init__(self, application: QApplication):
        super().__init__()
        print(f'Initialised Main Window, {self}')

        self.application = application
        self.engine = None
        self.stackedwidget = QStackedWidget()
        self.windowstack: list = []
        self.data = None

        self.setCentralWidget(self.stackedwidget)
        self.instantiateSubwindows()
        self.setCurrentSubwindow(1)

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
        self.stackedwidget.currentWidget().refresh(self.data)
        print(f'Subwindow change request, {self.stackedwidget.currentWidget()}')
        self.centreWindow()

    # Display previously opened sub window and remove
    # latest index from the stack
    def previousSubwindow(self) -> None:
        self.stackedwidget.currentWidget().closeWindows()
        self.stackedwidget.setCurrentIndex(self.windowstack[-1])
        self.stackedwidget.currentWidget().refresh(self.data)
        self.windowstack.pop()
        print(f'Subwindow change request, {self.stackedwidget.currentWidget()}')

    # Public method to close application
    def quitApplication(self) -> None:
        self.application.quit()

    # Override close event when window is manually closed
    def closeEvent(self, event: QCloseEvent):
        self.application.quit()
        return super().closeEvent(event)
    
    # Centres window
    def centreWindow(self) -> None:
        frame = self.frameGeometry()
        centre_point = self.screen().availableGeometry().center()
        frame.moveCenter(centre_point)
        self.move(frame.topLeft())

    def setData(self, data) -> None:
        self.data = data

    def initEngine(self, type: str, color: str, starting_fen: str, level: int, bullet: bool) -> None:
        'Initialises the chess engine.'
        self.engine = ChessEngine(type, level, color, Board(starting_fen), bullet)
    
    def requestEngineMove(self) -> str:
        'Returns the best engine move.'
        return self.engine.bestMove()

    def updateEngineFen(self, newfen) -> None:
        'Updates the position for the engine'
        self.engine.updatePosition(newfen)

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