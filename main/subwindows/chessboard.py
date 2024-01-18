# main/subwindows/chessboard.py

from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QCloseEvent, QKeyEvent
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
        self.firstmove: bool = False
        self.movelogflag: bool = False
        self.clock1: int = 75
        self.clock1_active: bool = False
        self.clock2: int = 75
        self.clock2_active: bool = False
        self.highlight: str = '#B0A7F6'
        self.highlight2: str = '#A49BE8'
        self.active_tile: bool = None
        self.active_piece: bool = None
        self.second_active: bool = None
        self.player1_color: str = 'white'
        self.hide_highlights = False

        self.render()

    # Render UI elements for subwindow
    def render(self) -> None:
        self.ui.initUI(self)
        self.ui.player1_time.setText(self.convertTime(self.clock1))
        self.ui.player2_time.setText(self.convertTime(self.clock2))
        self.importFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

        self.ui.exit_button.clicked.connect(self.openConfirmation)
        self.ui.settings_button.clicked.connect(self.openPreferences)

    # Open confirmation window
    def openConfirmation(self) -> None:
        if not self.windowstack:
            self.confirmwindow.show()
            self.windowstack.append(self.confirmwindow)
        else:
            self.confirmwindow.close()

    # Open preferences window
    def openPreferences(self) -> None:
        if not self.windowstack:
            self.preferenceswindow.show()
            self.windowstack.append(self.preferenceswindow)
        else:
            self.preferenceswindow.close()

    # Update window data
    def refresh(self) -> None:
        self.parent.setFixedSize(1000, 700)
        self.parent.setWindowTitle('Chessboard')

    # Imports FEN string
    def importFEN(self, fen: str) -> None:
        # Splits fen string into sections and sets variables
        self.fen = fen
        sections = fen.split(' ')
        self.piece_placement: str = sections[0]
        self.active_color: str = sections[1]
        self.castling_availability: str = sections[2]
        self.enpassant_square: str = sections[3]
        self.halfmove_clock: int = int(sections[4])
        self.fullmove_clock: int = int(sections[5])

        # Process piece placement data
        piece_ref = {'p': 'pawn', 'r': 'rook', 'b': 'bishop',
                     'n': 'knight','k': 'king', 'q': 'queen'}
        flip_digits = {1: 8, 2: 7, 3: 6, 4: 5,
                       5: 4, 6: 3, 7: 2, 8: 1}
        
        pieces = list(self.piece_placement)
        rank = 8
        file = 8
        for piece in pieces:
            if piece == '/':
                rank -= 1
                file = 8
            elif piece.isnumeric():
                file += int(piece)
            elif piece.lower() in piece_ref:
                pos = self.convertToPieceLayoutPos((flip_digits[file], flip_digits[rank]))
                tilepos = self.convertSquareNotation((file,rank))
                if piece.isupper():
                    self.placePiece(piece_ref[piece.lower()], 'black', pos, tilepos)
                else:
                    self.placePiece(piece_ref[piece], 'white', pos, tilepos)
                file -= 1

    # Returns new FEN string
    def exportFEN(self) -> str:
        piece_ref = {'pawn': 'p', 'rook': 'r', 'bishop': 'b',
                     'knight': 'n','king': 'k', 'queen': 'q'}
        pieces = []
        empty = 0
        a = 1
        rank = 8
        file = 8

        for i in range(64):
            if (i+1) == ((a * 8) + 1):
                if empty > 1:
                    pieces.append(str(empty))
                    empty = 0
                pieces.append('/')
                file = 8
                a += 1
                rank -= 1
                empty = 0
            piecepos = self.convertToPieceLayoutPos((file, rank))
            piecewidget = self.ui.piece_layout.itemAtPosition(piecepos[0], piecepos[1]).widget()
            if piecewidget.pieceInformation()[0] is None:
                empty += 1
                file -= 1
                continue
            piece = piece_ref[piecewidget.pieceInformation()[0]]
            if piecewidget.pieceInformation()[1] == 'black':
                piece = piece.upper()
            if empty != 0:
                pieces.append(str(empty))
                empty = 0
            pieces.append(piece)
            file -= 1

        pieces.append(' ')
        pieces.append(self.active_color)
        pieces.append(' ')
        pieces.append(self.castling_availability)
        pieces.append(' ')
        pieces.append(self.enpassant_square)
        pieces.append(' ')
        pieces.append(str(self.halfmove_clock))
        pieces.append(' ')
        pieces.append(str(self.fullmove_clock))

        fen = ''
        for char in pieces:
            fen += char
        
        return fen

    # Places pieces at specific position
    def placePiece(self, piece: str, color: str, pos: tuple, tilepos: str) -> None:
        'Places piece on existing empty widget.'
        piecewidget = self.ui.piece_layout.itemAtPosition(pos[0], pos[1]).widget()
        piecewidget.setPieceInformation(piece, color, tilepos)

    # Converts seconds to MM:SS format
    def convertTime(self, seconds) -> str:
        decimal = seconds / 60
        minutes = floor(decimal)
        seconds = seconds - (minutes * 60)
        if seconds > 9:
            seconds = str(seconds)
        else:
            seconds = f'0{str(seconds)}'
        if minutes > 9:
            minutes = str(minutes)
        else:
            minutes = f'0{str(minutes)}'
        
        return f'{minutes}:{seconds}'

    def convertToPieceLayoutPos(self, pos) -> tuple:
        'Converts square notation position (of either tuple or string) to layout position.'
        flip_digits = {1: 8, 2: 7, 3: 6, 4: 5,
                       5: 4, 6: 3, 7: 2, 8: 1}
        try:
            flip_digits[pos[0]]
            if isinstance(pos, tuple):
                pos = (pos[1], pos[0])
                pos = (flip_digits[pos[0]], pos[1])
                pos = (pos[0] - 1, pos[1] - 1)
                return pos
            elif isinstance(pos, str):
                pos = self.convertSquareNotation(pos)
                pos = (pos[1], pos[0])
                pos = (flip_digits[pos[0]], pos[1])
                pos = (pos[0] - 1, pos[1] - 1)
                return pos
            else:
                print(f'convertToPieceLayoutPos() error: {pos}')
                return None
        except KeyError as e:
            print(f'convertToPieceLayoutPos() error: {e}')
            return None

    # Updates timer 1 for timeController
    def update1(self):
        self.clock1 -= 1
        self.ui.player1_time.setText(self.convertTime(self.clock1))

        if self.clock1 == 0:
            self.timer1.stop()

    # Updates timer 2 for timeController
    def update2(self):
        self.clock2 -= 1
        self.ui.player2_time.setText(self.convertTime(self.clock2))

        if self.clock2 == 0:
            self.timer2.stop()

    # Controls the countdown and functionality of the timers
    def timeController(self) -> None:
        self.timer1 = QTimer()
        self.timer2 = QTimer()
        self.timer1.timeout.connect(self.update1)
        self.timer2.timeout.connect(self.update2)
        if not self.firstmove:
            if self.player1_color == 'white':
                self.timer1.start(1000)
                self.clock1_active = True
            else:
                self.timer2.start(1000)
                self.clock2_active = True

    # Switches timers
    def timeSwitch(self) -> None:
        if self.clock1_active:
            self.timer1.stop()
            self.timer2.start(1000)
            self.clock1_active = False
            self.clock2_active = True
            self.clock1 += 1
            self.ui.player1_time.setText(self.convertTime(self.clock1))
        elif self.clock2_active:
            self.timer2.stop()
            self.timer1.start(1000)
            self.clock1_active = True
            self.clock2_active = False
            self.clock2 += 1
            self.ui.player2_time.setText(self.convertTime(self.clock2))
        else:
            return

    # Executes upon mouse click
    def mousePressEvent(self, event: QKeyEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.click_pos = ( event.pos().x(), event.pos().y() )
            tile_pos = self.findTile(self.click_pos)
            if tile_pos is None:
                if self.active_tile is not None:
                    self.active_tile.resetColor()
                    self.active_tile = None
                return True
            tile = self.ui.board_layout.itemAtPosition(tile_pos[0], tile_pos[1]).widget()
            piece = self.ui.piece_layout.itemAtPosition(tile_pos[0], tile_pos[1]).widget()
            self.moveInputLogic(tile, piece)

    # Executes upon key press
    def keyPressEvent(self, event: QKeyEvent) -> None:
        # Minimise move log when 'M' is pressed
        if event.key() == Qt.Key.Key_M:
            if not self.movelogflag:
                self.ui.groupbox.hide()
                self.ui.divider.hide()
                self.ui.scrollarea.hide()
                self.ui.exit_button.hide()
                self.ui.settings_button.hide()
                self.parent.setFixedSize(620, 700)
                self.movelogflag = True
            else:
                self.ui.groupbox.show()
                self.ui.divider.show()
                self.ui.scrollarea.show()
                self.ui.exit_button.show()
                self.ui.settings_button.show()
                self.parent.setFixedSize(1000, 700)
                self.movelogflag = False

    # Handles moving and highlighting of pieces
    def moveInputLogic(self, tile, piece):
        'Moving and highlighting logic called by mousePressEvent().'
        # Resets highlighted tiles after recent move
        if self.second_active is not None:
            if self.active_tile is not None:
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
                    if not self.hide_highlights:
                        self.active_tile.setStyleSheet(f'background-color: {self.highlight}')
                else:
                    # Select another piece
                    self.active_tile.resetColor()
                    self.active_tile = tile
                    self.active_piece = piece
                    if not self.hide_highlights:
                        self.active_tile.setStyleSheet(f'background-color: {self.highlight}')
        # Check if selected piece is not the same as the player's colour
        elif piece.pieceInformation()[1] != self.player1_color:
            # If a piece is selected, move the piece
            if self.active_tile is not None:
                movepiece = self.movePiece(self.active_piece, piece)
                if movepiece:
                    self.second_active = tile
                    if not self.hide_highlights:
                        self.second_active.setStyleSheet(f'background-color: {self.highlight}')
                        self.active_tile.setStyleSheet(f'background-color: {self.highlight2}')
                else:
                    self.active_tile.resetColor()
                    self.active_tile = None
                    self.active_piece = None
        # Deselect tiles
        else:
            self.active_tile = None
            self.active_tile.resetColor()
            self.active_piece = None

    # Moves piece
    def movePiece(self, piece, target):
        'Sets target piece data to the piece that just captured.'
        pieceinfo = piece.pieceInformation()
        targetinfo = target.pieceInformation()
        valid = self.calculateValidSquares(piece)
        if targetinfo[2] in valid:
            piece.setPieceInformation(None, None, pieceinfo[2])
            target.setPieceInformation(pieceinfo[0], pieceinfo[1], targetinfo[2])
            targetinfo = target.pieceInformation()
            if (targetinfo[0] == 'pawn') and (not target.moved):
                target.moved = True
            # Switch active colour
            if self.active_color == 'w':
                self.player1_color = 'black'
                self.active_color = 'b'
            else:
                self.player1_color = 'white'
                self.active_color = 'w'
            # First move
            if not self.firstmove:
                self.timeController()
                self.firstmove = True
                return True
            self.timeSwitch()
            return True
        else:
            return False

    def getPieceInformationFromPos(self, tuplepos) -> tuple:
        'Returns data of a piece widget in the format (\'piece\', \'color\', \'a1\').'
        if (tuplepos[0] > 8 or tuplepos[0] < 1) or (tuplepos[1] > 8 or tuplepos[1] < 1):
            return (None, None, None)
        else:
            pos = self.convertToPieceLayoutPos((tuplepos[0], tuplepos[1]))
            piece = self.ui.piece_layout.itemAtPosition(pos[0], pos[1]).widget()
            return piece.pieceInformation()

    # Calculates valid squares for piece to move to
    def calculateValidSquares(self, piece) -> list:
        'Calculates valid squares (as tuples) based on the relative position of a piece.'
        tempvalid = []
        pieceinfo = piece.pieceInformation()
        pos: tuple = self.convertSquareNotation(pieceinfo[2])
        
        # Valid squares for pawn
        if pieceinfo[0] == 'pawn':
            if pieceinfo[1] == 'white':
                x = 1
            else:
                x = -1
            up = (pos[0], pos[1] + (1*x))
            two_up = (pos[0], pos[1] + (2*x))
            left_up = (pos[0] - 1, pos[1] + (1*x))
            right_up = (pos[0] + 1, pos[1] + (1*x))

            if (not piece.moved) and (not self.checkObstruction(two_up)) and (not self.checkObstruction(up)):
                tempvalid.append(two_up)
            if not self.checkObstruction(up):
                tempvalid.append(up)
            if self.checkObstruction(left_up):
                tempvalid.append(left_up)
            if self.checkObstruction(right_up):
                tempvalid.append(right_up)
        
        # Valid squares for knight
        if pieceinfo[0] == 'knight':
            tempvalid.append((pos[0]+1, pos[1]+2))
            tempvalid.append((pos[0]-1, pos[1]+2))
            tempvalid.append((pos[0]+1, pos[1]-2))
            tempvalid.append((pos[0]-1, pos[1]-2))
            tempvalid.append((pos[0]+2, pos[1]+1))
            tempvalid.append((pos[0]-2, pos[1]+1))
            tempvalid.append((pos[0]+2, pos[1]-1))
            tempvalid.append((pos[0]-2, pos[1]-1))

        # Remove squares outside of board and append to valid list
        valid = []
        print(tempvalid)
        for i in range(len(tempvalid)):
            try:
                square = tempvalid[i]
                print(square)
                if (square[0] > 8) or (square[1] > 8):
                    continue
                elif (square[0] < 1) or (square[1] < 1):
                    continue
                else:
                    valid.append(self.convertSquareNotation(square))
            except IndexError:
                continue
        
        print(valid)
        return valid
                
    def convertSquareNotation(self, x):
        'Converts string square notation (ie. a1) to tuple format (ie. 1, 1) and vice versa.'
        file_ref = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}
        reverse_file_ref = dict(map(reversed, file_ref.items()))
        if isinstance(x, str):
            return (file_ref[x[0]], int(x[1]))
        elif isinstance(x, tuple):
            return reverse_file_ref[x[0]] + str(x[1])
        else:
            return

    def checkObstruction(self, pos: tuple) -> bool:
        'Checks for piece at position'
        pos = self.convertToPieceLayoutPos(pos)
        if pos is not None:
            target = self.ui.piece_layout.itemAtPosition(pos[0], pos[1]).widget()
            targetinfo = target.pieceInformation()
            if targetinfo[0] is None:
                return False
            else:
                return True
        else:
            return True

    # Algorithm to find the column and row of the target tile
    def findTile(self, clickpos: tuple) -> tuple:
        'Finds the layout position of a tile based on click position.'
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
        x = end[0]
        y = end[1]
        overload = 0

        while True:
            if (clickpos[0] < x) and (clickpos[0] > x-70):
                targetvertex_x = x
                break
            else:
                overload += 1
                if (overload == 1000):
                    return None
                x -= 70
        while True:
            if (clickpos[1] < y) and (clickpos[1] > y-70):
                targetvertex_y = y
                break
            else:
                overload += 1
                if (overload == 1000):
                    return None
                y -= 70

        targetvertex_2 = (targetvertex_x, targetvertex_y)
        targetvertex_1 = (targetvertex_x - 70, targetvertex_y - 70)

        # Identify target tile
        for tile in tile_vertices:
            if (targetvertex_1 == tile[1]) and (targetvertex_2 == tile[2]):
                target_tile = tile[0]
                break

        # Identify tile file and rank
        flip_digits = {1: 8, 2: 7, 3: 6, 4: 5,
                       5: 4, 6: 3, 7: 2, 8: 1}
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

        return self.convertToPieceLayoutPos((flip_digits[f], flip_digits[r]))
    
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
        self.blindfoldflag = False
        self.highlightsflag = False

        self.render()

    # Render UI elements for the window
    def render(self) -> None:
        self.ui.initUI(self)
        self.setFixedSize(318, 244)
        self.setWindowTitle('Preferences')

        self.ui.theme_combo.currentIndexChanged.connect(self.changeTheme)
        self.ui.blindfold_checkbox.toggled.connect(self.blindfold)
        self.ui.highlights_checkbox.toggled.connect(self.hideHighlights)

    def hideHighlights(self) -> None:
            self.resetHighlights()
            self.parent.hide_highlights = not self.parent.hide_highlights
    
    def blindfold(self) -> None:
        if not self.blindfoldflag:
            for x in range(64):
                piece = self.parent.ui.piece_layout.itemAt(x).widget()
                piece.hide()
            self.blindfoldflag = True
        else:
            for x in range(64):
                piece = self.parent.ui.piece_layout.itemAt(x).widget()
                piece.show()
            self.blindfoldflag = False

    def resetHighlights(self) -> None:
        if self.parent.active_tile is not None:
            self.parent.active_tile.resetColor()
            self.parent.active_tile = None
        if self.parent.second_active is not None:
            self.parent.second_active.resetColor()
            self.parent.second_active = None
        self.parent.active_piece = None
    
    def changeTheme(self) -> None:
        index = self.ui.theme_combo.currentIndex()
        if index == 0:
            self.parent.highlight = '#B0A7F6'
            self.parent.highlight2 = '#A49BE8'
            self.resetHighlights()
            self.parent.ui.changeTheme('#E9EDF8', '#B9C0D6')
        if index == 1:
            self.parent.highlight = '#EAECA0'
            self.parent.highlight2 = '#E1E399'
            self.resetHighlights()
            self.parent.ui.changeTheme('#F1D9B4', '#DBBE9B')
        if index == 2:
            self.parent.highlight = '#F4F67F'
            self.parent.highlight2 = '#BBCC42'
            self.resetHighlights()
            self.parent.ui.changeTheme('#E9EDCC', '#779954')
        if index == 3:
            self.parent.highlight = '#A2D5FA'
            self.parent.highlight2 = '#7FA9C7'
            self.resetHighlights()
            self.parent.ui.changeTheme('#F0F3F4', '#727C8A')
    
    def closeWindow(self) -> None:
        self.parent.windowstack.pop()
        self.close()

    # Override close event when window is manually closed
    def closeEvent(self, event: QCloseEvent):
        self.parent.windowstack.pop()
        return super().closeEvent(event)