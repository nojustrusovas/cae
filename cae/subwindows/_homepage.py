# imports
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QMainWindow
from PySide6.QtGui import QFont, QIcon, QCloseEvent
from PySide6.QtCore import Qt

# define subwindow class
class SubWindow(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.game_init_window = GameInitWindow(False, self)
        self.practice_init_window = PracticeInitWindow(False, self)

    # init method when subwindow is shown
    def initWindow(self):
        self.parent.setWindowTitle('Homepage')
        self.parent.setFixedSize(450, 250)
        self.setUI()

        # button implementation
        self.quit_button.clicked.connect(self.parent.closeApplication) # close application
        self.play_button.clicked.connect(self.gameInit) # open game init window
        self.practice_button.clicked.connect(self.practiceInit) # open practice init window

    # set up UI elements
    def setUI(self):
        self.title = QLabel('Chess Application and Engine')
        font = QFont()
        font.setPointSize(25)
        font.setBold(True)
        self.title.setFont(font)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.play_button = QPushButton('Play')
        self.play_button.setFocusPolicy(Qt.NoFocus)
        self.practice_button = QPushButton('Practice')
        self.practice_button.setFocusPolicy(Qt.NoFocus)
        self.quit_button = QPushButton('Quit')
        self.quit_button.setFocusPolicy(Qt.NoFocus)
        self.horizontal_layout_widget = QWidget() # parent widget
        self.horizontal_layout = QHBoxLayout(self.horizontal_layout_widget) # make child
        self.horizontal_layout.addWidget(self.play_button)
        self.horizontal_layout.addWidget(self.practice_button)
        self.horizontal_layout.addWidget(self.quit_button)
        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.addWidget(self.title)
        self.vertical_layout.addWidget(self.horizontal_layout_widget)
        self.vertical_layout.setContentsMargins(50, 50, 50, 50)
        self.setLayout(self.vertical_layout) # set layout for window

    # shows GameInitWindow()
    def gameInit(self):
        if self.practice_init_window.active == False:
            self.game_init_window.show()
            self.game_init_window.setActiveState() # set state to active

    # shows PracticeInitWindow()
    def practiceInit(self):
        if self.game_init_window.active == False:
            self.practice_init_window.show()
            self.practice_init_window.setActiveState() # set state to active


class GameInitWindow(QMainWindow):
    def __init__(self, active, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle('Game initialisation')
        self.setWindowIcon(QIcon('icon.png'))
        self.setFixedSize(300, 100)
        self.active = active # bool to check if window is currently active
        self.setUI()

        # center window proportional to display dimensions
        frame = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())

        # button logic
        self.new_game_button.clicked.connect(self.sendWindowData)

    # set up UI elements
    def setUI(self):
        central_widget = QWidget()
        layout = QHBoxLayout()
        self.new_game_button = QPushButton('New Game')
        font = QFont()
        font.setBold(True)
        self.new_game_button.setFont(font)
        self.load_game_button = QPushButton('Load Game')
        layout.addWidget(self.new_game_button)
        layout.addWidget(self.load_game_button)
        layout.setContentsMargins(25, 0, 25, 0)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def sendWindowData(self):
        self.parent.parent.moveToWindow(1)
        self.close()
    
    # change active state of window
    def setActiveState(self):
        self.active = True

    # override close window event method to change active state
    def closeEvent(self, event: QCloseEvent) -> None:
        self.active = False # set state to inactive
        return super().closeEvent(event)


class PracticeInitWindow(QMainWindow):
    def __init__(self, active, parent):
        self.parent = parent
        super().__init__()
        self.setWindowTitle('Practice initialisation')
        self.setWindowIcon(QIcon('icon.png'))
        self.setFixedSize(300, 100)
        self.active = active # bool to check if window is currently active

        # center window proportional to display dimensions
        frame = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())

        # gui elements
        central_widget = QWidget()
        layout = QHBoxLayout()
        new_game_button = QPushButton('Analysis mode')
        font = QFont()
        font.setBold(True)
        new_game_button.setFont(font)
        load_game_button = QPushButton('Practice mode')
        layout.addWidget(new_game_button)
        layout.addWidget(load_game_button)
        layout.setContentsMargins(25, 0, 25, 0)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    # change active state of window
    def setActiveState(self):
        self.active = True

    # override close window event method to change active state
    def closeEvent(self, event: QCloseEvent) -> None:
        self.active = False # set state to inactive
        return super().closeEvent(event)