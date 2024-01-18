# main/subwindows/ui/chessboardui.py

from PySide6.QtWidgets import QWidget, QGridLayout, QGroupBox, QPushButton, QLabel, QScrollArea, QVBoxLayout, QStyleOption, QStyle, QComboBox, QCheckBox
from PySide6.QtGui import QFont, QPaintEvent, QPainter
from PySide6.QtCore import Qt, QRect, QMetaObject, QCoreApplication
from PySide6.QtSvgWidgets import QSvgWidget


class UI(object):
    def initUI(self, chessboard):
        if not chessboard.objectName():
            chessboard.setObjectName(u'chessboard')
        chessboard.resize(1000, 700)

        # Chessboard
        self.board = QWidget(chessboard)
        self.board.setObjectName(u'board')
        self.board.setGeometry(QRect(30, 65, 560, 560))
        self.board_layout = QGridLayout(self.board)
        self.board_layout.setContentsMargins(0, 0, 0, 0)
        self.board_layout.setSpacing(0)

        # Chess pieces
        self.board2 = QWidget(chessboard)
        self.board2.setObjectName(u'board2')
        self.board2.setGeometry(QRect(30, 65, 560, 560))
        self.piece_layout = QGridLayout(self.board2)
        self.piece_layout.setContentsMargins(0, 0, 0, 0)
        self.piece_layout.setSpacing(7)
        
        # Right group
        self.groupbox = QGroupBox(chessboard)
        self.groupbox.setGeometry(QRect(620, 30, 361, 631))
        self.groupbox.setTitle('')

        self.divider = QWidget(chessboard)
        self.divider.setGeometry(QRect(629, 75, 331, 1))
        self.divider.setStyleSheet(u"background-color: rgb(80, 80, 80);")

        # Scroll area / Move log
        self.scrollarea = QScrollArea(self.groupbox)
        self.scrollarea.setGeometry(QRect(9, 59, 341, 561))
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea_contents = QWidget()
        self.scrollarea_contents.setGeometry(QRect(0, 0, 339, 559))
        self.verticalLayout = QVBoxLayout(self.scrollarea_contents)
        self.scrollarea.setWidget(self.scrollarea_contents)

        # Buttons
        self.exit_button = QPushButton(chessboard)
        self.exit_button.setText('Exit')
        self.exit_button.setGeometry(QRect(630, 38, 51, 32))
        self.exit_button.setFocusPolicy(Qt.NoFocus)

        self.settings_button = QPushButton(chessboard)
        self.settings_button.setText('Settings')
        self.settings_button.setGeometry(QRect(690, 38, 71, 32))
        self.settings_button.setFocusPolicy(Qt.NoFocus)

        # Player 1
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        font2 = QFont()
        font2.setPointSize(20)
        font2.setBold(True)
        font3 = QFont()
        font3.setPointSize(11)
        font3.setItalic(True)

        self.player1_label = QLabel(chessboard)
        self.player1_label.setText('Player 1')
        self.player1_label.setGeometry(QRect(30, 640, 58, 16))
        self.player1_label.setFont(font)

        self.player1_time = QLabel(chessboard)
        self.player1_time.setText('00:00')
        self.player1_time.setGeometry(QRect(540, 640, 61, 20))
        self.player1_time.setFont(font2)

        # Player 2
        self.player2_label = QLabel(chessboard)
        self.player2_label.setText('Player 2')
        self.player2_label.setGeometry(QRect(30, 30, 58, 16))
        self.player2_label.setFont(font)

        self.engine_sublabel = QLabel(chessboard)
        self.engine_sublabel.setText('depth 2')
        self.engine_sublabel.setGeometry(QRect(80, 31, 58, 16))
        self.engine_sublabel.setFont(font3)
        self.engine_sublabel.hide()

        self.player2_time = QLabel(chessboard)
        self.player2_time.setText('00:00')
        self.player2_time.setGeometry(QRect(540, 30, 61, 20))
        self.player2_time.setFont(font2)

        self.drawTiles('#E9EDF8', '#B9C0D6')


    # Draw tiles and add to grid
    def drawTiles(self, col1, col2) -> None:
        self.col1 = col1 # Assign light tile colour as hex string
        self.col2 = col2 # Assign dark tile colour as hex string
        self.tile_size = (self.board.geometry().height() / 8, self.board.geometry().width() / 8)

        # Iterate through each rank and file and assign a tile
        flip_digits = {'1': '8', '2': '7', '3': '6', '4': '5',
                       '5': '4', '6': '3', '7': '2', '8': '1'}
        for row, rank in enumerate('12345678'):
            for col, file in enumerate('abcdefgh'):
                tile = Tile()
                tile.setObjectName(file + flip_digits[rank])
                tile.setFixedSize(self.tile_size[0], self.tile_size[1])
                if row % 2 == col % 2:
                    tile.setDefaultColor(self.col1)
                    tile.resetColor()
                else:
                    tile.setDefaultColor(self.col2)
                    tile.resetColor()

                self.board_layout.addWidget(tile, row, col)

                empty = Piece(None, None, file+flip_digits[rank])
                empty.setFixedSize(self.tile_size[0] - 14, self.tile_size[1] - 14)
                self.piece_layout.addWidget(empty, row, col)

    def changeTheme(self, light, dark):
        for row, rank in enumerate('12345678'):
            for col, file in enumerate('abcdefgh'):
                tile = self.board_layout.itemAtPosition(row, col).widget()
                if row % 2 == col % 2:
                    tile.setDefaultColor(light)
                    tile.resetColor()
                else:
                    tile.setDefaultColor(dark)
                    tile.resetColor()


class UI_ConfirmWindow(object):
    def initUI(self, confirmwindow):
        if not confirmwindow.objectName():
            confirmwindow.setObjectName(u'confirmwindow')
        confirmwindow.resize(318, 145)

        # Buttons
        self.yes_button = QPushButton(confirmwindow)
        self.yes_button.setObjectName(u"yes_button")
        self.yes_button.setGeometry(QRect(40, 90, 100, 32))

        self.no_button = QPushButton(confirmwindow)
        self.no_button.setObjectName(u"no_button")
        self.no_button.setGeometry(QRect(170, 90, 100, 32))
        self.no_button.setStyleSheet(u"color: rgb(255, 92, 91)")

        self.heading = QLabel(confirmwindow)
        self.heading.setObjectName(u"heading")
        self.heading.setGeometry(QRect(80, 40, 171, 16))

        self.retranslateUI(confirmwindow)
        QMetaObject.connectSlotsByName(confirmwindow)

    def retranslateUI(self, confirmwindow):
        confirmwindow.setWindowTitle(QCoreApplication.translate("confirmwindow", u"Form", None))
        self.yes_button.setText(QCoreApplication.translate("confirmwindow", u"Yes", None))
        self.heading.setText(QCoreApplication.translate("confirmwindow", u"Save game before exiting?", None))
        self.no_button.setText(QCoreApplication.translate("confirmwindow", u"No", None))


class UI_PreferencesWindow(object):
    def initUI(self, preferenceswindow):
        if not preferenceswindow.objectName():
            preferenceswindow.setObjectName(u'preferenceswindow')
        preferenceswindow.resize(318, 244)

        # Heading
        self.heading = QLabel(preferenceswindow)
        self.heading.setObjectName(u"heading")
        self.heading.setGeometry(QRect(20, 20, 241, 16))
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        self.heading.setFont(font)

        # Colour theme
        self.theme_sublabel = QLabel(preferenceswindow)
        self.theme_sublabel.setObjectName(u"theme_sublabel")
        self.theme_sublabel.setGeometry(QRect(20, 60, 91, 16))

        self.theme_combo = QComboBox(preferenceswindow)
        self.theme_combo.addItem("")
        self.theme_combo.addItem("")
        self.theme_combo.addItem("")
        self.theme_combo.addItem("")
        self.theme_combo.setObjectName(u"theme_combo")
        self.theme_combo.setGeometry(QRect(110, 54, 141, 32))

        # Subheading
        self.subheading = QLabel(preferenceswindow)
        self.subheading.setObjectName(u"subheading")
        self.subheading.setGeometry(QRect(20, 90, 131, 16))
        font2 = QFont()
        font2.setBold(True)
        self.subheading.setFont(font2)

        # Preferences
        self.movehints_checkbox = QCheckBox(preferenceswindow)
        self.movehints_checkbox.setObjectName(u"movehints_checkbox")
        self.movehints_checkbox.setGeometry(QRect(20, 120, 121, 20))

        self.highlights_checkbox = QCheckBox(preferenceswindow)
        self.highlights_checkbox.setObjectName(u"highlights_checkbox")
        self.highlights_checkbox.setGeometry(QRect(20, 150, 151, 20))

        self.blindfold_checkbox = QCheckBox(preferenceswindow)
        self.blindfold_checkbox.setObjectName(u"blindfold_checkbox")
        self.blindfold_checkbox.setGeometry(QRect(20, 180, 131, 20))

        self.sound_checkbox = QCheckBox(preferenceswindow)
        self.sound_checkbox.setObjectName(u"sound_checkbox")
        self.sound_checkbox.setGeometry(QRect(20, 210, 131, 20))

        self.retranslateUI(preferenceswindow)
        QMetaObject.connectSlotsByName(preferenceswindow)

    def retranslateUI(self, preferenceswindow):
        preferenceswindow.setWindowTitle(QCoreApplication.translate("preferenceswindow", u"Form", None))
        self.heading.setText(QCoreApplication.translate("preferenceswindow", u"Preferences and accessibility:", None))
        self.theme_sublabel.setText(QCoreApplication.translate("preferenceswindow", u"Colour theme:", None))
        self.theme_combo.setItemText(0, QCoreApplication.translate("preferenceswindow", u"Default", None))
        self.theme_combo.setItemText(1, QCoreApplication.translate("preferenceswindow", u"Classic", None))
        self.theme_combo.setItemText(2, QCoreApplication.translate("preferenceswindow", u"Green", None))
        self.theme_combo.setItemText(3, QCoreApplication.translate("preferenceswindow", u"High Contrast", None))
        self.theme_combo.setCurrentText(QCoreApplication.translate("preferenceswindow", u"Default", None))
        self.subheading.setText(QCoreApplication.translate("preferenceswindow", u"Visual preferences:", None))
        self.movehints_checkbox.setText(QCoreApplication.translate("preferenceswindow", u"Hide move hints", None))
        self.highlights_checkbox.setText(QCoreApplication.translate("preferenceswindow", u"Hide board highlights", None))
        self.blindfold_checkbox.setText(QCoreApplication.translate("preferenceswindow", u"Blindfold mode", None))
        self.sound_checkbox.setText(QCoreApplication.translate("preferenceswindow", u"Mute sound", None))


class Piece(QSvgWidget):
    def __init__(self, name: str, color: str, pos: str):
        super().__init__()
        self.name = name
        self.color = color
        self.pos = pos
        self.moved = False
        if name is not None:
            self.load('main/images/{}{}.svg'.format(self.color.lower(), self.name.lower()))

    def pieceInformation(self) -> tuple:
        return (self.name, self.color, self.pos)
    
    def setPieceInformation(self, name: str, color: str, pos: str):
        self.name = name
        self.color = color
        if name is not None:
            self.load('main/images/{}{}.svg'.format(self.color.lower(), self.name.lower()))
        else:
            self.load('main/images/none.svg')
    
    def setToHint(self) -> None:
        if self.name is None:
            self.load('main/images/defaulthint.svg')
        return

    def removeHint(self) -> None:
        if self.name is None:
             self.load('main/images/none.svg')
        return

class Tile(QWidget):
    def __init__(self):
        super().__init__()
        self.default_tile_color = None
    
    # Overrides paintEvent to allow style sheets
    # for this subclass of QWidget
    def paintEvent(self, event: QPaintEvent) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

    # Sets the default tile color for this tile
    def setDefaultColor(self, color) -> None:
        self.default_tile_color = color
    
    # Returns the default tile color for this tile
    def defaultColor(self) -> str:
        return self.default_tile_color
    
    # Sets the current color to default tile color
    def resetColor(self) -> None:
        self.setStyleSheet(f'background-color: {self.default_tile_color}')