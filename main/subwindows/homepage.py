# main/subwindows/homepage.py

from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtGui import QCloseEvent
from subwindows.ui import homepageui


class SubWindow(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__()
        self.parent = parent
        self.ui = homepageui.UI()
        self.windowstack: list = []
        self.practicewindow = PracticeWindow(self)

        self.render()

    # Render UI elements for sub window
    def render(self) -> None:
        self.ui.initUI(self)

        self.ui.quit_button.clicked.connect(self.parent.quitApplication)
        self.ui.play_button.clicked.connect(self.playMethod)
        self.ui.practice_button.clicked.connect(self.displayPracticeWindow)

    # Update window data
    def refresh(self) -> None:
        self.parent.setFixedSize(517, 295)
        self.parent.setWindowTitle('Homepage')

    # Displays a new specified sub window
    def playMethod(self) -> None:
        self.parent.setCurrentSubwindow(1)

    def displayPracticeWindow(self) -> None:
        self.practicewindow.show()
        self.windowstack.append(self.practicewindow)

    # Close all open windows before changing sub window
    def closeWindows(self) -> None:
        if len(self.windowstack) != 0:
            for window in self.windowstack:
                window.close()


class PracticeWindow(QMainWindow):
    def __init__(self, parent: QWidget):
        super().__init__()
        self.parent = parent
        self.setFixedSize(284, 100)
        self.setWindowTitle('Choose mode')
        self.ui = homepageui.PracticeWindowUI()
        self.ui.initUI(self)

    # Override close event when window is manually closed
    def closeEvent(self, event: QCloseEvent):
        self.parent.windowstack.pop()
        return super().closeEvent(event)