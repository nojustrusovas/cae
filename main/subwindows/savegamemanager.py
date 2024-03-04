# main/subwindows/savegamemanager.py

from PySide6.QtWidgets import QWidget, QMainWindow
from subwindows.ui import savegamemanagerui

class SubWindow(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__()
        self.parent = parent
        self.ui = savegamemanagerui.UI()
        self.windowstack: list = []

        self.render()
    
    def render(self) -> None:
        self.ui.initUI(self)

    def refresh(self, data) -> None:
        self.parent.setFixedSize(900, 600)
        self.parent.setWindowTitle('Save game manager')