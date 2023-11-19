# imports
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QMainWindow, QGridLayout
from PySide6.QtWidgets import QFrame, QComboBox, QCheckBox, QLineEdit, QSpinBox, QSpacerItem
from PySide6.QtGui import QFont, QCloseEvent, QPainter
from PySide6.QtCore import Qt

# define sub window class
class SubWindow(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    
    # init method when subwindow is shown
    def initWindow(self):
        self.parent.setWindowTitle('New Game')
        self.parent.setFixedSize(600, 600)
        self.setUI()

    # set up UI elements
    def setUI(self):
        self.board = QWidget()
        self.board_layout = QGridLayout(self.board)
        self.board_layout.setContentsMargins(0, 0, 0, 0)
        self.board_layout.setSpacing(0)
        self.drawTiles('#F0D9B5', '#B58863')

        self.setLayout(self.board_layout)

    # draw tiles on screen
    def drawTiles(self, col1, col2):
        self.col1 = col1 # assign dark tile colour as hex string
        self.col2 = col2 # assign light tile colour as hex string

        # iterate through each rank and file and draw a tile
        for row, rank in enumerate('12345678'):
            for col, file in enumerate('abcdefgh'):
                tile = QWidget()
                tile.setObjectName(file + rank)
                tile.setFixedSize(40, 40)
                if row % 2 == col % 2: # check if row and column are both odd or both even
                    tile.setStyleSheet(f'background-color: {self.col1}') # assign dark tile
                else:
                    tile.setStyleSheet(f'background-color: {self.col2}') # assign light tile
                self.board_layout.addWidget(tile, row, col) # add tile to grid layout
            