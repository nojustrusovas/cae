# imports
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QMainWindow
from PySide6.QtWidgets import QFrame, QComboBox, QCheckBox, QLineEdit, QSpinBox, QSpacerItem
from PySide6.QtGui import QFont, QCloseEvent
from PySide6.QtCore import Qt

# define sub window class
class SubWindow(QWidget):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.info_window = InfoWindow(False, self)

    # reset UI values when sub window is shown
    def initWindow(self):
        self.parent.setWindowTitle('New Game Configuration')
        self.parent.setFixedSize(521, 382)
        self.setUI()

        # logic implementation
        self.gametype_combo.currentIndexChanged.connect(self.updateUI)
        self.fen_checkbox.stateChanged.connect(self.updateUI)
        self.back_button.clicked.connect(self.backButton)
        self.start_button.clicked.connect(self.finishConfig)
    
    # set up UI elements
    def setUI(self):
        self.vertical_layout = QVBoxLayout()

        self.row1 = QWidget()
        self.row1_layout = QHBoxLayout(self.row1)
        self.back_button = QPushButton('Back')
        self.back_button.setFocusPolicy(Qt.NoFocus)
        self.back_button.setFixedSize(71, 32)
        self.row1_layout.addWidget(self.back_button)

        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.HLine)
        self.divider.setFrameShadow(QFrame.Plain)
        self.title = QLabel('Configurations')
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.title.setFont(font)

        self.row2 = QWidget()
        self.row2.setFixedHeight(50)
        self.row2_layout = QHBoxLayout(self.row2)
        self.row2_layout.setSpacing(0)
        self.row2.setContentsMargins(0, 0, 130, 0)
        self.gametype_label = QLabel('Game type:')
        font = QFont()
        font.setBold(True)
        self.gametype_label.setFont(font)
        self.gametype_label.setFixedWidth(80)
        self.gametype_combo = QComboBox()
        self.gametype_combo.setEditable(False)
        self.gametype_combo.setFocusPolicy(Qt.NoFocus)
        self.gametype_combo.addItem('Solo Play')
        self.gametype_combo.addItem('Two Player')
        self.gametype_combo.setCurrentIndex(0)
        self.gametype_combo.setToolTip('Select whether the game is played solo against the engine, or against a second local player.')
        self.gametype_combo.setToolTipDuration(100 * 1000) # 100 seconds
        self.depth_label = QLabel('Engine Depth:')
        self.depth_label.setFixedWidth(100)
        self.depth_spinbox = QSpinBox()
        self.depth_spinbox.setMinimum(1)
        self.depth_spinbox.setMaximum(6)
        self.depth_spinbox.setFocusPolicy(Qt.NoFocus)
        self.depth_spinbox.setFixedWidth(40)
        self.depth_spinbox.setToolTip('1 - Easy, 6 - Expert')
        self.depth_spinbox.setToolTipDuration(100 * 1000) # 100 seconds
        self.row2_layout.addWidget(self.gametype_label)
        self.row2_layout.addWidget(self.gametype_combo)
        self.row2_layout.addSpacerItem(QSpacerItem(20, 5))
        self.row2_layout.addWidget(self.depth_label)
        self.row2_layout.addWidget(self.depth_spinbox)

        self.row3 = QWidget()
        self.row3_layout = QHBoxLayout(self.row3)
        self.row3.setContentsMargins(0, 0, 240, 0)
        self.format_label = QLabel('Time Format:')
        self.format_label.setFixedWidth(86)
        self.format_combo = QComboBox()
        self.format_combo.setEditable(False)
        self.format_combo.setFocusPolicy(Qt.NoFocus)
        self.format_combo.addItem('Unlimited')
        self.format_combo.addItem('Classic (60min)')
        self.format_combo.addItem('Rapid (10min)')
        self.format_combo.addItem('Blitz (5min)')
        self.format_combo.addItem('Bullet (2min)')
        self.format_combo.setToolTip('Select the time format the game is played.')
        self.format_combo.setToolTipDuration(100 * 1000) # 100 seconds
        self.row3_layout.addWidget(self.format_label)
        self.row3_layout.addWidget(self.format_combo)

        self.row4 = QWidget()
        self.row4.setContentsMargins(0, 0, 340, 0)
        self.row4_layout = QHBoxLayout(self.row4)
        self.fen_checkbox = QCheckBox()
        self.fen_checkbox.setText('Custom FEN')
        self.fen_checkbox.setFocusPolicy(Qt.NoFocus)
        self.fen_checkbox.setToolTip('Optionally start from a custom position using a valid FEN string.')
        self.fen_checkbox.setToolTipDuration(100 * 1000) # 100 seconds
        self.fen_entry = QLineEdit()
        self.fen_entry.setFixedHeight(20)
        self.fen_entry.setReadOnly(False)
        font = QFont()
        font.setPointSize(10)
        self.fen_entry.setFont(font)
        self.fen_entry.hide()
        self.fen_entry.setToolTip('Only include the first section of the FEN string.')
        self.fen_entry.setToolTipDuration(10 * 1000) # 3 seconds
        self.row4_layout.addWidget(self.fen_checkbox)
        self.row4_layout.addSpacerItem(QSpacerItem(20, 5))
        self.row4_layout.addWidget(self.fen_entry)

        self.row5 = QWidget()
        self.row5.setContentsMargins(0, 0, 350, 0)
        self.row5_layout = QHBoxLayout(self.row5)
        self.startas_label = QLabel('Start as:')
        self.startas_label.setFixedWidth(50)
        self.startas_combo = QComboBox()
        self.startas_combo.setEditable(False)
        self.startas_combo.setFocusPolicy(Qt.NoFocus)
        self.startas_combo.setFixedWidth(80)
        self.startas_combo.addItem('White')
        self.startas_combo.addItem('Black')
        self.startas_combo.setToolTip('Start as a specified colour if playing against the engine.')
        self.startas_combo.setToolTipDuration(100 * 1000) # 100 seconds
        self.row5_layout.addWidget(self.startas_label)
        self.row5_layout.addWidget(self.startas_combo)

        self.start_button = QPushButton('Start Game')
        font = QFont()
        font.setBold(True)
        self.start_button.setFont(font)
        self.start_button.setFixedWidth(100)

        self.vertical_layout.addWidget(self.back_button)
        self.vertical_layout.addWidget(self.divider)
        self.vertical_layout.addWidget(self.title)
        self.vertical_layout.addWidget(self.row2)
        self.vertical_layout.addWidget(self.row3)
        self.vertical_layout.addWidget(self.row4)
        self.vertical_layout.addWidget(self.row5)
        self.vertical_layout.addSpacerItem(QSpacerItem(5, 20))
        self.vertical_layout.addWidget(self.start_button)
        self.vertical_layout.addSpacerItem(QSpacerItem(5, 20))
        self.setLayout(self.vertical_layout)

    # back button logic
    def backButton(self):
        if self.info_window.active == False:
            self.parent.previousWindow()

    # update ui elements
    def updateUI(self):
        # hide depth label and combo if solo play is not selected
        if self.gametype_combo.currentIndex() == 0:
            self.depth_label.show()
            self.depth_spinbox.show()
            self.row2.setContentsMargins(0, 0, 130, 0)
        elif self.gametype_combo.currentIndex() == 1:
            self.depth_label.hide()
            self.depth_spinbox.hide()
            self.row2.setContentsMargins(0, 0, 250, 0)
        
        # hide fen string entry if custom fen is not checked
        if self.fen_checkbox.isChecked():
            self.fen_entry.show()
            self.row4.setContentsMargins(0, 0, 100, 0)
        else:
            self.fen_entry.hide()
            self.row4.setContentsMargins(0, 0, 340, 0)

    # final validation and finish configuration
    def finishConfig(self):
        if self.info_window.active == False: # check if no info window is displayed
            if self.fen_checkbox.isChecked():
                if self.validateFEN(self.fen_entry.text()): fen = self.fen_entry.text() # if fen valid then assign the new string,
                else: fen = None # else set invalid flag
            else:
                fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' # default starting position
            
            if fen == None: self.invalidFEN() # open info window
            else:
                # valid configurations to send as data
                self.configurations = (self.gametype_combo.currentIndex(), self.format_combo.currentIndex(), fen, self.startas_combo.currentIndex())

    # validates custom FEN string
    def validateFEN(self, fen: str) -> bool:
        fen = fen.strip()
        fen = fen.split(' ')
        fen = fen[0]
        if fen.count('/') != 7: return False # checks for 7 breaks
        if (fen[0] == '/') or (fen[-1] == '/'): return False # checks for break at start and end
        try: fen.index('//'); return False # checks for repeated breaks
        except: pass

        # check for total value of 8 for each row
        valid_chars = ['p', 'r', 'n', 'b', 'q', 'k']
        fen_segments = fen.split('/')
        for segment in fen_segments:
            segment_value = 0
            chars = list(segment)
            for char in chars:
                if char.isalpha():
                    segment_value += 1
                    if char.lower() in valid_chars: pass # check for valid characters
                    else: return False
                elif char.isnumeric():
                    segment_value += int(char)
                    if (int(char) > 0) and (int(char) < 9): pass # check for valid integers
                    else: return False
                else: return False # prevents non alpha-numeric characters
            if segment_value != 8: return False
        
        if (fen.count('k') != 1) or (fen.count('K') != 1): return False # check for a king for both sides

        return True
    
    # display info window with invalid fen text
    def invalidFEN(self):
        if self.info_window.active == False:
            self.info_window.show()
            self.info_window.setActiveState() # set state to active


# info window
class InfoWindow(QMainWindow):
    def __init__(self, active, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle('Error')
        self.setFixedSize(200, 100)
        self.active = active # bool to check if window is currently active
        self.setUI()

        # center window proportional to display dimensions
        frame = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())

        # button logic
        self.ok_button.clicked.connect(self.closeWindow)

    # set up UI elements
    def setUI(self):
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.label = QLabel('Invalid FEN string entered.')
        self.ok_button = QPushButton('OK')
        self.ok_button.setFixedWidth(50)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.ok_button)
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    # change active state of window
    def setActiveState(self):
        self.active = True

    # override close window event method to change active state
    def closeEvent(self, event: QCloseEvent) -> None:
        self.active = False # set state to inactive
        return super().closeEvent(event)
    
    # close window
    def closeWindow(self):
        self.active = False # set state to inactive
        self.close()