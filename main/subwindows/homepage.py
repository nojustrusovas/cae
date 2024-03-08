# main/subwindows/homepage.py

from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtGui import QCloseEvent
from subwindows.ui import homepageui
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl, QEvent


class SubWindow(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__()
        self.parent = parent
        self.ui = homepageui.UI()
        self.windowstack: list = []
        self.practicewindow = PracticeWindow(self)

        # Sound
        self.s_hover = QSoundEffect()
        self.s_hover.setSource(QUrl.fromLocalFile("main/audio/buttonhover.wav"))
        self.s_hover.setVolume(0.3)

        self.render()

    # Render UI elements for sub window
    def render(self) -> None:
        self.ui.initUI(self)
        self.ui.play_button.installEventFilter(self)
        self.ui.practice_button.installEventFilter(self)
        self.ui.quit_button.installEventFilter(self)

        #self.ui.quit_button.clicked.connect(self.parent.quitApplication)
        #self.ui.play_button.clicked.connect(self.playMethod)
        #self.ui.practice_button.clicked.connect(self.displayPracticeWindow)

    # Update window data
    def refresh(self, data) -> None:
        self.parent.setFixedSize(517, 295)
        self.parent.setWindowTitle('Homepage')

    # Play button hover sound
    def buttonHover(self) -> None:
        self.s_hover.play()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            self.buttonHover()
        elif event.type() == QEvent.MouseButtonPress:
                if obj.objectName() == 'Play':
                    self.playMethod()
                elif obj.objectName() == 'Practice':
                    pass
                elif obj.objectName() == 'Quit':
                    self.parent.quitApplication()
        return False

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