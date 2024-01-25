# main/subwindows/chessboard.py

from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QTimer, Qt, QUrl
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
        self.mutesound = False
        self.blindfold = False
        self.hidehints = False
        self.occupied: bool = False
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
        self.hints = []
        self.kingpos: dict = {'white': None, 'black': None}
        self.check = False
        self.check_tile = (None, None)
        self.enpassant_color = None
        self.pawn_promote = None
        self.hintname = 'defaulthint'
        self.hintcapturename = 'defaulthintcapture'

        # Sound variables
        self.s_move = QSoundEffect()
        self.s_move.setSource(QUrl.fromLocalFile("main/audio/move-self.wav"))
        self.s_capture = QSoundEffect()
        self.s_capture.setSource(QUrl.fromLocalFile("main/audio/capture.wav"))
        self.s_check = QSoundEffect()
        self.s_check.setSource(QUrl.fromLocalFile("main/audio/move-check.wav"))
        self.s_castle = QSoundEffect()
        self.s_castle.setSource(QUrl.fromLocalFile("main/audio/castle.wav"))
        self.s_promote = QSoundEffect()
        self.s_promote.setSource(QUrl.fromLocalFile("main/audio/promote.wav"))

        self.render()

    # Render UI elements for subwindow
    def render(self) -> None:
        self.ui.initUI(self)
        self.ui.player1_time.setText(self.convertTime(self.clock1))
        self.ui.player2_time.setText(self.convertTime(self.clock2))
        self.importFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

        if self.player1_color == 'white':
            self.ui.player1_label.setStyleSheet('color: #FFFFFF')
            self.ui.player1_time.setStyleSheet('color: #FFFFFF')
            self.ui.player2_label.setStyleSheet('color: #404040')
            self.ui.player2_time.setStyleSheet('color: #404040')
        else:
            self.ui.player2_label.setStyleSheet('color: #FFFFFF')
            self.ui.player2_time.setStyleSheet('color: #FFFFFF')
            self.ui.player1_label.setStyleSheet('color: #404040')
            self.ui.player1_time.setStyleSheet('color: #404040')

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

    def pawnPromoteRequest(self, piecename) -> None:
        pawninfo = self.pawn_promote.pieceInformation()
        self.pawn_promote.setPieceInformation(piecename, pawninfo[1], pawninfo[2])
        if self.blindfold is False:
            self.pawn_promote.pieceShow()
        self.ui.pawnPromotion(pawninfo[2])
        if self.mutesound is False:
            self.s_promote.play()
        self.occupied = False
        self.pawn_promote = None

    def returnKingPosition(self) -> dict:
        x = self.kingpos
        return x

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
                tilepos = self.convertSquareNotation((flip_digits[file], flip_digits[rank]))
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

    def canCastle(self, castletype: str) -> bool:
        '''Checks to see if the king can castle depending on the parameter passed. 
        K: white kingside, Q: white queenside, k: black kingside, q: black queenside.'''
        # White kingside
        if castletype == 'K':
            checkifempty = ['f1', 'g1']
            rookpos = self.convertToPieceLayoutPos((8, 1))
            rookwidget = self.ui.piece_layout.itemAtPosition(rookpos[0], rookpos[1]).widget()
            rookinfo = rookwidget.pieceInformation()
            kingpos = self.convertToPieceLayoutPos((5, 1))
            kingwidget = self.ui.piece_layout.itemAtPosition(kingpos[0], kingpos[1]).widget()
            kinginfo = kingwidget.pieceInformation()
            # Checks tiles inbetween are empty
            for tile in checkifempty:
                pos = self.convertSquareNotation(tile)
                pos = self.convertToPieceLayoutPos(pos)
                widget = self.ui.piece_layout.itemAtPosition(pos[0], pos[1]).widget()
                widgetinfo = widget.pieceInformation()
                if widgetinfo[0] is not None:
                    return False
            # Checks that rook and king are in the correct position and have not moved
            if (kinginfo[0] != 'king') or (kingwidget.moved is True) or (kinginfo[1] != 'white'):
                return False
            if (rookinfo[0] != 'rook') or (rookwidget.moved is True) or (rookinfo[1] != 'white'):
                return False
            # Else allow the castle
            return True
        # White queenside
        if castletype == 'Q':
            checkifempty = ['b1', 'c1', 'd1']
            rookpos = self.convertToPieceLayoutPos((1, 1))
            rookwidget = self.ui.piece_layout.itemAtPosition(rookpos[0], rookpos[1]).widget()
            rookinfo = rookwidget.pieceInformation()
            kingpos = self.convertToPieceLayoutPos((5, 1))
            kingwidget = self.ui.piece_layout.itemAtPosition(kingpos[0], kingpos[1]).widget()
            kinginfo = kingwidget.pieceInformation()
            # Checks tiles inbetween are empty
            for tile in checkifempty:
                pos = self.convertSquareNotation(tile)
                pos = self.convertToPieceLayoutPos(pos)
                widget = self.ui.piece_layout.itemAtPosition(pos[0], pos[1]).widget()
                widgetinfo = widget.pieceInformation()
                if widgetinfo[0] is not None:
                    return False
            # Checks that rook and king are in the correct position and have not moved
            if (kinginfo[0] != 'king') or (kingwidget.moved is True) or (kinginfo[1] != 'white'):
                return False
            if (rookinfo[0] != 'rook') or (rookwidget.moved is True) or (rookinfo[1] != 'white'):
                return False
            # Else allow the castle
            return True
        # Black kingside
        if castletype == 'k':
            checkifempty = ['f8', 'g8']
            rookpos = self.convertToPieceLayoutPos((8, 8))
            rookwidget = self.ui.piece_layout.itemAtPosition(rookpos[0], rookpos[1]).widget()
            rookinfo = rookwidget.pieceInformation()
            kingpos = self.convertToPieceLayoutPos((5, 8))
            kingwidget = self.ui.piece_layout.itemAtPosition(kingpos[0], kingpos[1]).widget()
            kinginfo = kingwidget.pieceInformation()
            # Checks tiles inbetween are empty
            for tile in checkifempty:
                pos = self.convertSquareNotation(tile)
                pos = self.convertToPieceLayoutPos(pos)
                widget = self.ui.piece_layout.itemAtPosition(pos[0], pos[1]).widget()
                widgetinfo = widget.pieceInformation()
                if widgetinfo[0] is not None:
                    return False
            # Checks that rook and king are in the correct position and have not moved
            if (kinginfo[0] != 'king') or (kingwidget.moved is True) or (kinginfo[1] != 'black'):
                return False
            if (rookinfo[0] != 'rook') or (rookwidget.moved is True) or (rookinfo[1] != 'black'):
                return False
            # Else allow the castle
            return True
        # Black queenside
        if castletype == 'q':
            checkifempty = ['b8', 'c8', 'd8']
            rookpos = self.convertToPieceLayoutPos((1, 8))
            rookwidget = self.ui.piece_layout.itemAtPosition(rookpos[0], rookpos[1]).widget()
            rookinfo = rookwidget.pieceInformation()
            kingpos = self.convertToPieceLayoutPos((5, 8))
            kingwidget = self.ui.piece_layout.itemAtPosition(kingpos[0], kingpos[1]).widget()
            kinginfo = kingwidget.pieceInformation()
            # Checks tiles inbetween are empty
            for tile in checkifempty:
                pos = self.convertSquareNotation(tile)
                pos = self.convertToPieceLayoutPos(pos)
                widget = self.ui.piece_layout.itemAtPosition(pos[0], pos[1]).widget()
                widgetinfo = widget.pieceInformation()
                if widgetinfo[0] is not None:
                    return False
            # Checks that rook and king are in the correct position and have not moved
            if (kinginfo[0] != 'king') or (kingwidget.moved is True) or (kinginfo[1] != 'black'):
                return False
            if (rookinfo[0] != 'rook') or (rookwidget.moved is True) or (rookinfo[1] != 'black'):
                return False
            # Else allow the castle
            return True
        
        # Edge case
        return False

    # Places pieces at specific position
    def placePiece(self, piece: str, color: str, pos: tuple, tilepos: str) -> None:
        'Places piece on existing empty widget.'
        piecewidget = self.ui.piece_layout.itemAtPosition(pos[0], pos[1]).widget()
        piecewidget.setPieceInformation(piece, color, tilepos)
        if self.blindfold is False:
            piecewidget.pieceShow()

        # Update kingpos
        pieceinfo = piecewidget.pieceInformation()
        if (pieceinfo[0] == 'king') and (pieceinfo[1] == 'white'):
            self.kingpos['white'] = pieceinfo[2]
        elif (pieceinfo[0] == 'king') and (pieceinfo[1] == 'black'):
            self.kingpos['black'] = pieceinfo[2]
        
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
            if isinstance(pos, str):
                pos = self.convertSquareNotation(pos)
                pos = (pos[1], pos[0])
                pos = (flip_digits[pos[0]], pos[1])
                pos = (pos[0] - 1, pos[1] - 1)
                return pos
            elif isinstance(pos, tuple):
                pos = (pos[1], pos[0])
                pos = (flip_digits[pos[0]], pos[1])
                pos = (pos[0] - 1, pos[1] - 1)
                return pos
            else:
                return None
        except KeyError:
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
                self.ui.player1_label.setStyleSheet('color: #FFFFFF')
                self.ui.player1_time.setStyleSheet('color: #FFFFFF')
                self.ui.player2_label.setStyleSheet('color: #404040')
                self.ui.player2_time.setStyleSheet('color: #404040')
            else:
                self.timer2.start(1000)
                self.clock2_active = True
                self.ui.player2_label.setStyleSheet('color: #FFFFFF')
                self.ui.player2_time.setStyleSheet('color: #FFFFFF')
                self.ui.player1_label.setStyleSheet('color: #404040')
                self.ui.player1_time.setStyleSheet('color: #404040')

    # Switches timers
    def timeSwitch(self) -> None:
        if self.clock1_active:
            self.timer1.stop()
            self.timer2.start(1000)
            self.clock1_active = False
            self.clock2_active = True
            self.clock1 += 1
            self.ui.player1_time.setText(self.convertTime(self.clock1))
            self.ui.player2_label.setStyleSheet('color: #FFFFFF')
            self.ui.player2_time.setStyleSheet('color: #FFFFFF')
            self.ui.player1_label.setStyleSheet('color: #404040')
            self.ui.player1_time.setStyleSheet('color: #404040')
        elif self.clock2_active:
            self.timer2.stop()
            self.timer1.start(1000)
            self.clock1_active = True
            self.clock2_active = False
            self.clock2 += 1
            self.ui.player2_time.setText(self.convertTime(self.clock2))
            self.ui.player1_label.setStyleSheet('color: #FFFFFF')
            self.ui.player1_time.setStyleSheet('color: #FFFFFF')
            self.ui.player2_label.setStyleSheet('color: #404040')
            self.ui.player2_time.setStyleSheet('color: #404040')
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
                    self.hideHints()
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
    def moveInputLogic(self, tile, piece) -> None:
        'Moving and highlighting logic called by mousePressEvent().'
        if self.occupied:
            return
        
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
            if self.active_tile == tile:
                # Deselect if the same tile is selected again
                self.hideHints()
                self.active_tile.resetColor()
                self.active_tile = None
                self.active_piece = None
            else:
                # Select new piece
                valid = self.calculateValidMoves(piece)
                self.showHints(valid, piece)
                if self.active_tile is None:
                    self.active_tile = tile
                    self.active_piece = piece
                    if not self.hide_highlights:
                        self.active_tile.setStyleSheet(f'background-color: {self.highlight}')
                else:
                    # Select another piece
                    self.hideHints()
                    valid = self.calculateValidMoves(piece)
                    self.showHints(valid, piece)
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
                    self.hideHints()
                    self.active_tile.resetColor()
                    self.active_tile = None
                    self.active_piece = None
        # Deselect tiles
        else:
            self.hideHints()
            self.active_tile = None
            self.active_tile.resetColor()
            self.active_piece = None

    def checkFunc(self, kingcolor) -> None:
        'Code to run during an active check'
        self.checked_king = kingcolor
        pos = self.kingpos[self.checked_king]
        pos = self.convertSquareNotation(pos)
        pos = self.convertToPieceLayoutPos(pos)
        tile = self.ui.board_layout.itemAtPosition(pos[0], pos[1]).widget()
        self.check_tile = (tile, tile.defaultColor())
        self.check_tile[0].setDefaultColor('#FF3838')
        self.check_tile[0].resetColor()
        if self.mutesound is False:
            self.s_check.play()

    # Moves piece
    def movePiece(self, piece, target) -> None:
        'Sets target piece data to the piece that just captured /  moved.'
        flip = {'white': 'black', 'black': 'white'}
        pieceinfo = piece.pieceInformation()
        targetinfo = target.pieceInformation()
        valid = self.calculateValidMoves(piece)
        if targetinfo[2] in valid:
            # Sound
            if self.mutesound is False:
                if targetinfo[0] is None:
                    self.s_move.play()
                else:
                    self.s_capture.play()
            self.hideHints()

            # Castle check
            if (pieceinfo[0] == 'king') and (targetinfo[2] in piece.castlemoves):
                if pieceinfo[1] == 'white' and targetinfo[2] == 'g1':
                    target2 = self.ui.piece_layout.itemAtPosition(7, 7).widget()
                    target2.setPieceInformation(None, None, 'h1')
                    if self.blindfold is False:
                        target2.pieceShow()
                    target2 = self.ui.piece_layout.itemAtPosition(7, 5).widget()
                    target2.setPieceInformation('rook', 'white', 'f1')
                    if self.blindfold is False:
                        target2.pieceShow()
                    self.active_tile.resetColor()
                    self.active_tile = self.ui.board_layout.itemAtPosition(7, 5).widget()
                elif pieceinfo[1] == 'white' and targetinfo[2] == 'c1':
                    target2 = self.ui.piece_layout.itemAtPosition(7, 0).widget()
                    target2.setPieceInformation(None, None, 'a1')
                    if self.blindfold is False:
                        target2.pieceShow()
                    target2 = self.ui.piece_layout.itemAtPosition(7, 3).widget()
                    target2.setPieceInformation('rook', 'white', 'd1')
                    if self.blindfold is False:
                        target2.pieceShow()
                    self.active_tile.resetColor()
                    self.active_tile = self.ui.board_layout.itemAtPosition(7, 3).widget()
                elif pieceinfo[1] == 'black' and targetinfo[2] == 'g8':
                    target2 = self.ui.piece_layout.itemAtPosition(0, 7).widget()
                    target2.setPieceInformation(None, None, 'h8')
                    if self.blindfold is False:
                        target2.pieceShow()
                    target2 = self.ui.piece_layout.itemAtPosition(0, 5).widget()
                    target2.setPieceInformation('rook', 'black', 'f8')
                    if self.blindfold is False:
                        target2.pieceShow()
                    self.active_tile.resetColor()
                    self.active_tile = self.ui.board_layout.itemAtPosition(0, 5).widget()
                elif pieceinfo[1] == 'black' and targetinfo[2] == 'c8':
                    target2 = self.ui.piece_layout.itemAtPosition(0, 0).widget()
                    target2.setPieceInformation(None, None, 'a8')
                    if self.blindfold is False:
                        target2.pieceShow()
                    target2 = self.ui.piece_layout.itemAtPosition(0, 3).widget()
                    target2.setPieceInformation('rook', 'black', 'd8')
                    if self.blindfold is False:
                        target2.pieceShow()
                    self.active_tile.resetColor()
                    self.active_tile = self.ui.board_layout.itemAtPosition(0, 3).widget()
                if self.mutesound is False:
                    self.s_castle.play()
            piece.setPieceInformation(None, None, pieceinfo[2])
            target.setPieceInformation(pieceinfo[0], pieceinfo[1], targetinfo[2])
            if self.blindfold is False:
                piece.pieceShow()
                target.pieceShow()
            targetinfo = target.pieceInformation()

            # En passant
            if targetinfo[0] == 'pawn':
                currentpos = self.convertSquareNotation(targetinfo[2])
                lastpos = self.convertSquareNotation(pieceinfo[2])
                change = (currentpos[0] - lastpos[0], currentpos[1] - lastpos[1])
                # Check to see if pawn just made a two place advance, if so set the target square
                if (change[0] == 0) and ((change[1] == 2) or (change[1] == -2)):
                    target.two_moved = True
                    enpassant = self.convertSquareNotation(targetinfo[2])
                    if targetinfo[1] == 'white':
                        enpassant = (enpassant[0], enpassant[1] - 1)
                    else:
                        enpassant = (enpassant[0], enpassant[1] + 1)
                    enpassant = self.convertSquareNotation(enpassant)
                    self.enpassant_square = enpassant # Set enpassant square
                    self.enpassant_color = targetinfo[1]
                # Check to see if pawn is trying to initiate an enpassant
                elif targetinfo[2] == self.enpassant_square:
                    enpassant = self.convertSquareNotation(targetinfo[2])
                    if targetinfo[1] == 'white':
                        enpassant = (enpassant[0], enpassant[1] - 1)
                    else:
                        enpassant = (enpassant[0], enpassant[1] + 1)
                    targetenpassant = self.convertToPieceLayoutPos(enpassant)
                    capturepiece = self.ui.piece_layout.itemAtPosition(targetenpassant[0], targetenpassant[1]).widget()
                    enpassant = self.convertSquareNotation(enpassant)
                    capturepiece.setPieceInformation(None, None, enpassant)
                    if self.blindfold is False:
                        capturepiece.pieceShow()
                    self.enpassant_square = '-'
                    self.enpassant_color = None
                    if self.mutesound is False:
                        self.s_capture.play()
                # Reset enpassant target square
                else:
                    self.enpassant_square = '-'    
                    self.enpassant_color = None

                # Pawn promotion
                pawnrank = self.convertSquareNotation(targetinfo[2])[1]
                if (targetinfo[1] == 'white') and (pawnrank == 8):
                    self.showPawnPromotion(target, 'white')
                elif (targetinfo[1] == 'black') and (pawnrank == 1):
                    self.showPawnPromotion(target, 'black')

            # Check highlight
            possiblechecks = self.calculateValidSquares(target)
            oppositeking = flip[targetinfo[1]]
            if self.check is True:
                self.check_tile[0].setDefaultColor(self.check_tile[1])
                self.check_tile[0].resetColor()
                self.check = False
            if self.kingpos[oppositeking] in possiblechecks:
                self.check = True
                self.checkFunc(flip[targetinfo[1]])
            else:
                # Discovered check
                for i in range(64):
                    widget = self.ui.piece_layout.itemAt(i).widget()
                    widgetinfo = widget.pieceInformation()
                    if widgetinfo[0] is None:
                        continue
                    if widgetinfo[1] == targetinfo[1]:
                        checksquares = self.calculateValidSquares(widget)
                        if self.kingpos[oppositeking] in checksquares:
                            self.check = True
                            self.checkFunc(flip[widgetinfo[1]])
                            print(flip[widgetinfo[1]])
                            break
                    else:
                        continue
            
            if targetinfo[0] == 'king':
                target.moved = True
            if (targetinfo[0] == 'pawn') and (not target.moved):
                target.moved = True
            if targetinfo[0] == 'king':
                self.kingpos[targetinfo[1]] = targetinfo[2]
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

    def calculateValidMoves(self, piece) -> list:
        'Returns a list of valid moves after check and move validation'
        pieceinfo = piece.pieceInformation()
        tempvalid = self.calculateValidSquares(piece)
        originalkingpos = {'white': None, 'black': None}
        originalkingpos['white'] = self.kingpos['white']
        originalkingpos['black'] = self.kingpos['black']
        invalid = []
        valid = []
        for move in tempvalid:
            # Set target square / piece
            pos = self.convertSquareNotation(move)
            pos = self.convertToPieceLayoutPos(pos)
            target = self.ui.piece_layout.itemAtPosition(pos[0], pos[1]).widget()
            targetinfo = target.pieceInformation()

            # Do the move
            tempstore1 = piece.pieceInformation()
            tempstore2 = targetinfo
            if pieceinfo[0] == 'king':
                self.kingpos[pieceinfo[1]] = move
            piece.setPieceInformation(None, None, pieceinfo[2])
            target.setPieceInformation(pieceinfo[0], pieceinfo[1], targetinfo[2])

            # Identify check
            flip = {'white': 'black', 'black': 'white'}
            for i in range(64):
                widget = self.ui.piece_layout.itemAt(i).widget()
                widgetinfo = widget.pieceInformation()
                if widgetinfo[1] == flip[pieceinfo[1]]:
                    checksquares = self.calculateValidSquares(widget)
                    if self.kingpos[pieceinfo[1]] in checksquares:
                        invalid.append(move)
                        break
                else:
                    continue
                
            # Reset move
            piece.setPieceInformation(tempstore1[0], tempstore1[1], tempstore1[2])
            target.setPieceInformation(tempstore2[0], tempstore2[1], tempstore2[2])
            self.kingpos['white'] = originalkingpos['white']
            self.kingpos['black'] = originalkingpos['black']

        if invalid:
            for move in tempvalid:
                if move in invalid:
                    continue
                else:
                    valid.append(move)
            return valid
        else:
            return tempvalid
            
    def showHints(self, validmoves: list, piece) -> None:
        'Method to show hints on board'
        if self.hidehints is False:
            for valid in validmoves:
                pos = self.convertSquareNotation(valid)
                pos = self.convertToPieceLayoutPos(pos)
                widget = self.ui.piece_layout.itemAtPosition(pos[0], pos[1]).widget()
                widget2 = self.ui.hint_layout.itemAtPosition(pos[0], pos[1]).widget()
                pieceinfo = piece.pieceInformation()
                widgetinfo = widget.pieceInformation()
                a = widget.setToHint(self.hintname)
                if a:
                    self.hints.append(widget)
                elif pieceinfo[1] != widgetinfo[1]:
                    widget2.showHint()
                    self.hints.append(widget2)

    def hideHints(self) -> None:
        'Method to hide all hints on the board'
        for hint in self.hints:
            hint.removeHint()
        self.hints = []

    def showPawnPromotion(self, pawn, color) -> None:
        self.occupied = True
        self.ui.pawnPromotion(color)
        self.pawn_promote = pawn

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
        'Calculates valid squares (as square notation) based on the relative position of a piece.'
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
            # En passant check
            try:
                left_up = self.convertSquareNotation(left_up)
                right_up = self.convertSquareNotation(right_up)
                if self.enpassant_color != pieceinfo[1]:
                    if left_up == self.enpassant_square:
                        tempvalid.append((pos[0] - 1, pos[1] + (1*x)))
                    elif right_up == self.enpassant_square:
                        tempvalid.append((pos[0] + 1, pos[1] + (1*x)))
            except Exception:
                pass
        
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

        # Valid squares for bishop or queen
        if (pieceinfo[0] == 'bishop') or (pieceinfo[0] == 'queen'):
            tl_continuous = True
            tr_continuous = True
            bl_continuous = True
            br_continuous = True

            for i in range(1, 7):
                tl = (pos[0] - (1*i), pos[1] + (1*i))
                tr = (pos[0] + (1*i), pos[1] + (1*i))
                bl = (pos[0] - (1*i), pos[1] - (1*i))
                br = (pos[0] + (1*i), pos[1] - (1*i))

                if tl_continuous:
                    tempvalid.append(tl)
                if tr_continuous:
                    tempvalid.append(tr)
                if bl_continuous:
                    tempvalid.append(bl)
                if br_continuous:
                    tempvalid.append(br)

                if self.checkObstruction(tl):
                    tl_continuous = False
                if self.checkObstruction(tr):
                    tr_continuous = False
                if self.checkObstruction(bl):
                    bl_continuous = False
                if self.checkObstruction(br):
                    br_continuous = False

        # Valid squares for rook or queen
        if (pieceinfo[0] == 'rook') or (pieceinfo[0] == 'queen'):
            up_continuous = True
            down_continuous = True
            left_continuous = True
            right_continuous = True

            for i in range(1, 7):
                up = (pos[0], pos[1] + (1*i))
                down = (pos[0], pos[1] - (1*i))
                left = (pos[0] - (1*i), pos[1])
                right = (pos[0] + (1*i), pos[1])

                if up_continuous:
                    tempvalid.append(up)
                if down_continuous:
                    tempvalid.append(down)
                if left_continuous:
                    tempvalid.append(left)
                if right_continuous:
                    tempvalid.append(right)

                if self.checkObstruction(up):
                    up_continuous = False
                if self.checkObstruction(down):
                    down_continuous = False
                if self.checkObstruction(left):
                    left_continuous = False
                if self.checkObstruction(right):
                    right_continuous = False

         # Valid squares for king
        if pieceinfo[0] == 'king':
            tempvalid.append((pos[0]+1, pos[1]))
            tempvalid.append((pos[0]-1, pos[1]))
            tempvalid.append((pos[0]+1, pos[1]+1))
            tempvalid.append((pos[0]+1, pos[1]-1))
            tempvalid.append((pos[0]-1, pos[1]+1))
            tempvalid.append((pos[0]-1, pos[1]-1))
            tempvalid.append((pos[0], pos[1]+1))
            tempvalid.append((pos[0], pos[1]-1))

            # Check for castles
            piece.castlemoves = []
            if pieceinfo[1] == 'white':
                if self.canCastle('K'):
                    position = (pos[0]+2, pos[1])
                    tempvalid.append(position)
                    position = self.convertSquareNotation(position)
                    piece.castlemoves.append(position)
                if self.canCastle('Q'):
                    position = (pos[0]-2, pos[1])
                    tempvalid.append(position)
                    position = self.convertSquareNotation(position)
                    piece.castlemoves.append(position)
            elif pieceinfo[1] == 'black':
                if self.canCastle('k'):
                    position = (pos[0]+2, pos[1])
                    tempvalid.append(position)
                    position = self.convertSquareNotation(position)
                    piece.castlemoves.append(position)
                if self.canCastle('q'):
                    position = (pos[0]-2, pos[1])
                    tempvalid.append(position)
                    position = self.convertSquareNotation(position)
                    piece.castlemoves.append(position)

        # Remove squares outside of board and append to valid list
        valid = []
        for i in range(len(tempvalid)):
            try:
                square = tempvalid[i]
                if (square[0] > 8) or (square[1] > 8):
                    continue
                elif (square[0] < 1) or (square[1] < 1):
                    continue
                else:
                    valid.append(self.convertSquareNotation(square))
            except IndexError:
                continue
        
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
        self.hintsflag = False
        self.soundflag = False

        self.render()

    # Render UI elements for the window
    def render(self) -> None:
        self.ui.initUI(self)
        self.setFixedSize(318, 244)
        self.setWindowTitle('Preferences')

        self.ui.theme_combo.currentIndexChanged.connect(self.changeTheme)
        self.ui.blindfold_checkbox.toggled.connect(self.blindfold)
        self.ui.highlights_checkbox.toggled.connect(self.hideHighlights)
        self.ui.movehints_checkbox.toggled.connect(self.moveHints)
        self.ui.sound_checkbox.toggled.connect(self.muteSound)

    def muteSound(self) -> None:
        if not self.soundflag:
            self.parent.mutesound = True
            self.soundflag = True
        else:
            self.parent.mutesound = False
            self.soundflag = False

    def moveHints(self) -> None:
        if not self.hintsflag:
            self.parent.hideHints()
            self.parent.hidehints = True
            self.hintsflag = True
        else:
            self.parent.hidehints = False
            self.hintsflag = False

    def hideHighlights(self) -> None:
            self.resetHighlights()
            self.parent.hide_highlights = not self.parent.hide_highlights
    
    def blindfold(self) -> None:
        if not self.blindfoldflag:
            for x in range(64):
                piece = self.parent.ui.piece_layout.itemAt(x).widget()
                piece.pieceHide()
            self.blindfoldflag = True
            self.parent.blindfold = True
        else:
            for x in range(64):
                piece = self.parent.ui.piece_layout.itemAt(x).widget()
                piece.pieceShow()
            self.blindfoldflag = False
            self.parent.blindfold = False

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
            self.parent.hintname = 'defaulthint'
            self.parent.hintcapturename = 'defaulthintcapture'
            self.parent.ui.changeTheme('#E9EDF8', '#B9C0D6')
        if index == 1:
            self.parent.highlight = '#EAECA0'
            self.parent.highlight2 = '#E1E399'
            self.parent.hintname = 'classichint'
            self.parent.hintcapturename = 'classiccapture'
            self.parent.ui.changeTheme('#F1D9B4', '#DBBE9B')
        if index == 2:
            self.parent.highlight = '#F4F67F'
            self.parent.highlight2 = '#BBCC42'
            self.parent.hintname = 'yellowhint'
            self.parent.hintcapturename = 'yellowcapture'
            self.parent.ui.changeTheme('#E9EDCC', '#779954')
        if index == 3:
            self.parent.highlight = '#A2D5FA'
            self.parent.highlight2 = '#7FA9C7'
            self.parent.hintname = 'contrasthint'
            self.parent.hintcapturename = 'contrastcapture'
            self.parent.ui.changeTheme('#F0F3F4', '#727C8A')
        if not self.parent.hide_highlights:
            if self.parent.second_active is not None:
                self.parent.second_active.setStyleSheet(f'background-color: {self.parent.highlight}')
            if self.parent.active_tile is not None:
                self.parent.active_tile.setStyleSheet(f'background-color: {self.parent.highlight2}')
        for i in range(64):
            hintwidget = self.parent.ui.hint_layout.itemAt(i).widget()
            hintwidget.changeDefault(self.parent.hintcapturename)
        for hint in self.parent.hints:
            if isinstance(hint, chessboardui.Hint):
                hint.removeHint()
                hint.showHint()
            else:
                hint.setToHint(self.parent.hintname)
    
    def closeWindow(self) -> None:
        self.parent.windowstack.pop()
        self.close()

    # Override close event when window is manually closed
    def closeEvent(self, event: QCloseEvent):
        self.parent.windowstack.pop()
        return super().closeEvent(event)