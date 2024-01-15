# main/subwindows/chessboard.py

from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QCloseEvent
from subwindows.ui import chessboardui
from math import floor


class SubWindow(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__()
        self.parent = parent
        self.ui = chessboardui.UI()
        self.windowstack: list = []
        self.confirmwindow = ConfirmWindow(self)
        self.preferenceswindow = PreferencesWindow(self)

        # Board variables
        self.duration: int = 75
        self.active_tile: bool = None
        self.active_piece: bool = None
        self.second_active: bool = None
        self.player1_color: str = 'white'

        self.render()
        self.timeController()

    # Render UI elements for subwindow
    def render(self) -> None:
        self.ui.initUI(self)
        self.ui.player1_time.setText(self.convertTime(self.duration))

        self.ui.exit_button.clicked.connect(self.openConfirmation)
        self.ui.settings_button.clicked.connect(self.openPreferences)

    def openConfirmation(self) -> None:
        if not self.windowstack:
            self.confirmwindow.show()
            self.windowstack.append(self.confirmwindow)

    def openPreferences(self) -> None:
        if not self.windowstack:
            self.preferenceswindow.show()
            self.windowstack.append(self.preferenceswindow)

    # Update window data
    def refresh(self) -> None:
        self.parent.setFixedSize(1000, 700)
        self.parent.setWindowTitle('Chessboard')

    # Converts seconds to MM:SS format
    def convertTime(self, seconds) -> str:
        decimal = self.duration / 60
        minutes = floor(decimal)
        seconds = self.duration - (minutes * 60)
        if seconds > 9:
            seconds = str(seconds)
        else:
            seconds = f'0{str(seconds)}'
        if minutes > 9:
            minutes = str(minutes)
        else:
            minutes = f'0{str(minutes)}'
        
        return f'{minutes}:{seconds}'

    # Updates timer for timeController
    def update(self):
        self.duration -= 1
        self.ui.player1_time.setText(self.convertTime(self.duration))

        if self.duration == 0:
            self.timer.stop()

    # Controls the countdown and functionality of the timers
    def timeController(self) -> None:
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

# Executes upon mouse click
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.click_pos = ( event.pos().x(), event.pos().y() )
            tile_pos = self.findTile(self.click_pos)
            if tile_pos is None:
                if self.active_tile is not None:
                    self.active_tile.resetColor()
                    self.active_tile = None
                return True
            tile = self.ui.board_layout.itemAtPosition(tile_pos[1], tile_pos[0]).widget()
            piece = self.ui.piece_layout.itemAtPosition(tile_pos[1], tile_pos[0]).widget()

            # Resets highlighted tiles after recent move
            if self.second_active is not None:
                self.active_tile.resetColor()
                self.active_tile = None
                self.active_piece = None
                self.second_active.resetColor()
                self.second_active = None
            # Check if selected piece is the same as the player's colour
            if piece.pieceInformation()[1] == self.player1_color:
                # Deselect if the same tile is selected again
                if self.active_tile == tile:
                    self.active_tile.resetColor()
                    self.active_tile = None
                    self.active_piece = None
                else:
                    # Select new piece
                    if self.active_tile is None:
                        self.active_tile = tile
                        self.active_piece = piece
                        self.active_tile.setStyleSheet('background-color: #B0A7F6')
                    else:
                        # Select another piece
                        self.active_tile.resetColor()
                        self.active_tile = tile
                        self.active_piece = piece
                        self.active_tile.setStyleSheet('background-color: #B0A7F6')
            # Check if selected piece is not the same as the player's colour
            elif piece.pieceInformation()[1] != self.player1_color:
                # If a piece is selected, move the piece
                if self.active_tile is not None:
                    self.moveTile(self.active_piece, piece)
                    self.second_active = tile
                    self.second_active.setStyleSheet('background-color: #B0A7F6')
                    self.active_tile.setStyleSheet('background-color: #A49BE8')
            # Deselect tiles
            else:
                self.active_tile = None
                self.active_piece = None

        return True

    # Moves piece
    def moveTile(self, piece, target):
        pieceinfo = piece.pieceInformation()
        targetinfo = piece.pieceInformation()
        piece.setPieceInformation(None, None, pieceinfo[2])
        target.setPieceInformation(pieceinfo[0], pieceinfo[1], targetinfo[2])

    # Algorithm to find the column and row of the target tile
    def findTile(self, clickpos):
        origin = (31,68) # To be changed
        end = (origin[0] + (70 * 8), origin[1] + (70 * 8))

        # Validate clickpos is within board
        if (clickpos[0] < origin[0]) or (clickpos[0] > end[0]):
            return None
        elif (clickpos[1] < origin[1]) or (clickpos[1] > end[1]):
            return None
        else:
            pass

        # Calculate tile vertices
        tile_vertices = []
        if tile_vertices == []:
            tile_num = 1
            for x in range(8):
                for y in range(8):
                    vertex1 = ( origin[0] + (70 * x), origin[1] + (70 * y) )
                    vertex2 = ( origin[0] + (70 * x) + 70, origin[1] + (70 * y) + 70)
                    tile_vertices.append((tile_num, vertex1, vertex2))
                    tile_num += 1

        # Identify target vertex
        targetvertex_x = 0
        x = end[0]
        targetvertex_y = 0
        y = end[1]

        while True:
            if (clickpos[0] < x) and (clickpos[0] > x-70):
                targetvertex_x = x
                break
            else:
                x -= 70
        while True:
            if (clickpos[1] < y) and (clickpos[1] > y-70):
                targetvertex_y = y
                break
            else:
                y -= 70

        targetvertex_2 = (targetvertex_x, targetvertex_y)
        targetvertex_1 = (targetvertex_x - 70, targetvertex_y - 70)

        # Identify target tile
        for tile in tile_vertices:
            if (targetvertex_1 == tile[1]) and (targetvertex_2 == tile[2]):
                target_tile = tile[0]
                break

        # Identify tile file and rank
        f = 8
        r = 1
        for i in range(64):
            if (i+1) == target_tile:
                break
            if r == 8:
                f -= 1
                r = 1
            else:
                r += 1
        flip_digits = {1: 8, 2: 7, 3: 6, 4: 5,
                       5: 4, 6: 3, 7: 2, 8: 1}
        tile_pos = (flip_digits[f]-1, r-1)
        return tile_pos
    
    def closeWindows(self) -> None:
        for window in self.windowstack:
            window.close()
    

class ConfirmWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.ui = chessboardui.UI_ConfirmWindow()

        self.render()

    # Render UI elements for the window
    def render(self) -> None:
        self.ui.initUI(self)
        self.setFixedSize(318, 145)
        self.setWindowTitle('Confirm')

        self.ui.yes_button.clicked.connect(self.closeWindow)
        self.ui.no_button.clicked.connect(self.closeWindow)

    def closeWindow(self) -> None:
        self.close()
        self.parent.parent.setCurrentSubwindow(0)

    # Override close event when window is manually closed
    def closeEvent(self, event: QCloseEvent):
        self.parent.windowstack.pop()
        return super().closeEvent(event)


class PreferencesWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.ui = chessboardui.UI_PreferencesWindow()

        self.render()

    # Render UI elements for the window
    def render(self) -> None:
        self.ui.initUI(self)
        self.setFixedSize(318, 244)
        self.setWindowTitle('Preferences')

    def closeWindow(self) -> None:
        self.parent.windowstack.pop()
        self.close()

    # Override close event when window is manually closed
    def closeEvent(self, event: QCloseEvent):
        self.parent.windowstack.pop()
        return super().closeEvent(event)