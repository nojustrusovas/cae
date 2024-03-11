# main/subwindows/chessboard.py

from PySide6.QtWidgets import QWidget, QMainWindow, QApplication
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QTimer, Qt, QUrl, QEvent, QThread
from PySide6.QtGui import QCloseEvent, QKeyEvent
from subwindows.ui import chessboardui
from math import floor


class EngineThread(QThread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        'Run expensive operation'
        self.parent.engineMove()

class SubWindow(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__()
        self.parent = parent
        self.ui = chessboardui.UI()
        self.windowstack: list = []
        self.confirmwindow = ConfirmWindow(self)
        self.preferenceswindow = PreferencesWindow(self)

        # Board variables
        self.gametype = None
        self.mutesound = False
        self.blindfold = False
        self.hidehints = False
        self.occupied: bool = False
        self.firstmove: bool = False
        self.movelogflag: bool = False
        self.clock1: int = None
        self.clock1_active: bool = False
        self.clock2: int = None
        self.clock2_active: bool = False
        self.highlight: str = '#B0A7F6'
        self.highlight2: str = '#A49BE8'
        self.active_tile: bool = None
        self.active_piece: bool = None
        self.second_active: bool = None
        self.hide_highlights = False
        self.hints = []
        self.kingpos: dict = {'white': None, 'black': None}
        self.check = False
        self.check_tile = (None, None)
        self.enpassant_color = None
        self.pawn_promote = None
        self.hintname = 'defaulthint'
        self.hintcapturename = 'defaulthintcapture'
        self.is_checkmate = False
        self.move_log = {}
        self.move_log_pointer = 0
        self.current_notation = None
        self.current_log = []
        self.board_position_history = []
        self.to_resign = None
        self.will_promote = False
        self.enginereq = (None, None)
        self.enginedidpromote = False

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
        self.s_hover = QSoundEffect()
        self.s_hover.setSource(QUrl.fromLocalFile("main/audio/buttonhover.wav"))
        self.s_hover.setVolume(0.3)
        self.s_end = QSoundEffect()
        self.s_end.setSource(QUrl.fromLocalFile("main/audio/game-end.wav"))

        self.render()

    # Render UI elements for subwindow
    def render(self) -> None:
        self.ui.initUI(self)

        self.ui.view_button.installEventFilter(self)
        self.ui.analyse_button.installEventFilter(self)
        self.ui.save_button.installEventFilter(self)
        self.ui.settings_button.installEventFilter(self)
        self.ui.exit_button.installEventFilter(self)
        self.ui.resign_button.installEventFilter(self)
        self.ui.draw_button.installEventFilter(self)
        self.ui.copyfen_button.installEventFilter(self)

    # Open confirmation window
    def openConfirmation(self, conf) -> None:
        if not self.windowstack:
            self.confirmwindow.setConfirmation(conf)
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
    def refresh(self, data) -> None:
        self.parent.setFixedSize(1000, 700)
        self.parent.setWindowTitle('Chessboard')
        self.resetVariables()
        self.board_position_history = []
        self.current_log = []
        self.move_log = {}
        self.move_log_pointer = 0
        self.clock1_active: bool = False
        self.clock2_active: bool = False
        self.occupied: bool = False
        self.firstmove: bool = False
        self.movelogflag: bool = False
        self.enginetomove = False
        self.engineactive = False
        self.enginerequest = None

        self.ui.clearBoard()
        self.ui.clearLog()
        self.ui.clearCaptures()

        # Set chessboard configurations
        configurations = data[0]
        if configurations is None:
            return
        else:
            # Init data file for this game
            if data[1] is False:
                self.parent.newANIIL(configurations)
            else:
                self.parent.loadANIIL(data[2])

            self.player1_name = configurations[4]
            self.player2_name = configurations[5]
            if configurations[6] is not None:
                self.clock1 = configurations[6]
                self.clock2 = configurations[9]
                self.no_time_limit = False
            else:
                self.noTimeLimit()
            self.player1_color =  configurations[7]

            self.importFEN(configurations[8])

            if not self.no_time_limit:
                self.ui.player1_time.setText(self.convertTime(self.clock1))
                self.ui.player2_time.setText(self.convertTime(self.clock2))
            if self.player1_color == 'black':
                self.ui.player2_label.setText(self.player1_name)
                self.ui.player1_label.setText(self.player2_name)
            else:
                self.ui.player1_label.setText(self.player1_name)
                self.ui.player2_label.setText(self.player2_name)

            if self.active_color == 'b':
                self.current_log.append('-')
                self.move_log_pointer += 1
                self.move_log[self.move_log_pointer] = self.current_log[0]
                self.updateMoveLog(False)
                self.ui.player2_label.setStyleSheet('color: #FFFFFF')
                self.ui.player2_time.setStyleSheet('color: #FFFFFF')
                self.ui.player1_label.setStyleSheet('color: #404040')
                self.ui.player1_time.setStyleSheet('color: #404040')
            else:
                self.ui.player1_label.setStyleSheet('color: #FFFFFF')
                self.ui.player1_time.setStyleSheet('color: #FFFFFF')
                self.ui.player2_label.setStyleSheet('color: #404040')
                self.ui.player2_time.setStyleSheet('color: #404040')

            if configurations[0] == 0:
                self.gametype = 'engine'
                if self.active_color == 'b' and self.player1_color == 'white':
                    self.engineactive = True
                    self.engine_thread = EngineThread(self)
                    self.engine_thread.finished.connect(self.engineMoveRequest)
                    self.engine_thread.start()
                elif self.active_color == 'b' and self.player1_color == 'black':
                    self.engineactive = False
                elif self.active_color == 'w' and self.player1_color == 'black':
                    self.engineactive = True
                    self.engine_thread = EngineThread(self)
                    self.engine_thread.finished.connect(self.engineMoveRequest)
                    self.engine_thread.start()
                elif self.active_color == 'w' and self.player1_color == 'white':
                    self.engineactive = False
            else:
                self.gametype = 'player'

            self.board_position_history.append(self.saveBoardPosition())

    def resetVariables(self) -> None:
        'Resets variables to their init state.'
        self.gametype = None
        self.mutesound = False
        self.blindfold = False
        self.hidehints = False
        self.occupied: bool = False
        self.firstmove: bool = False
        self.movelogflag: bool = False
        self.clock1: int = None
        self.clock1_active: bool = False
        self.clock2: int = None
        self.clock2_active: bool = False
        self.highlight: str = '#B0A7F6'
        self.highlight2: str = '#A49BE8'
        self.active_tile: bool = None
        self.active_piece: bool = None
        self.second_active: bool = None
        self.hide_highlights = False
        self.hints = []
        self.kingpos: dict = {'white': None, 'black': None}
        self.check = False
        self.check_tile = (None, None)
        self.enpassant_color = None
        self.pawn_promote = None
        self.hintname = 'defaulthint'
        self.hintcapturename = 'defaulthintcapture'
        self.is_checkmate = False
        self.move_log = {}
        self.move_log_pointer = 0
        self.current_notation = None
        self.current_log = []
        self.board_position_history = []
        self.to_resign = None
        self.will_promote = False
        self.enginereq = (None, None)
        self.enginedidpromote = False

    # If cursor hovers over widget
    def buttonHover(self, index) -> None:
        if index == 1:
            self.s_hover.play()
        if index == 2:
            self.ui.exit_button.load('main/images/exit-hover.svg')
        if index == 3:
            self.ui.settings_button.load('main/images/settings-hover.svg')
        if index == 4:
            self.ui.resign_button.load('main/images/resign-hover.svg')
        if index == 5:
            self.ui.draw_button.load('main/images/draw-hover.svg')
        if index == 6:
            self.ui.copyfen_button.load('main/images/copy-hover.svg')
    
    # If cursor leaves widget
    def buttonUnHover(self, index) -> None:
        if index == 1:
            self.ui.exit_button.load('main/images/exit.svg')
        if index == 2:
            self.ui.settings_button.load('main/images/settings.svg')
        if index == 3:
            self.ui.resign_button.load('main/images/resign.svg')
        if index == 4:
            self.ui.draw_button.load('main/images/draw.svg')
        if index == 5:
            self.ui.copyfen_button.load('main/images/copy.svg')

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            if (obj.objectName() == 'View') or (obj.objectName() == 'Analyse') or (obj.objectName() == 'Save'):
                self.buttonHover(1)
            elif obj.objectName() == 'Exit':
                self.buttonHover(2)
            elif obj.objectName() == 'Settings':
                self.buttonHover(3)
            elif obj.objectName() == 'Resign':
                self.buttonHover(4)
            elif obj.objectName() == 'Draw':
                self.buttonHover(5)
            elif obj.objectName() == 'Copy FEN':
                self.buttonHover(6)
        elif event.type() == QEvent.Leave:
            if obj.objectName() == 'Exit':
                self.buttonUnHover(1)
            elif obj.objectName() == 'Settings':
                self.buttonUnHover(2)
            elif obj.objectName() == 'Resign':
                self.buttonUnHover(3)
            elif obj.objectName() == 'Draw':
                self.buttonUnHover(4)
            elif obj.objectName() == 'Copy FEN':
                self.buttonUnHover(5)
        elif event.type() == QEvent.MouseButtonPress:
                if obj.objectName() == 'View':
                    self.ui.checkmatewidget.hide()
                elif obj.objectName() == 'Analyse':
                    pass
                elif obj.objectName() == 'Save':
                    self.close()
                    self.parent.setCurrentSubwindow(0)
                elif obj.objectName() == 'Settings':
                    self.openPreferences()
                elif obj.objectName() == 'Exit':
                    self.openConfirmation(0)
                elif obj.objectName() == 'Resign':
                    if not self.occupied:
                        self.openConfirmation(1)
                elif obj.objectName() == 'Draw':
                    if not self.occupied:
                        self.openConfirmation(2)
                elif obj.objectName() == 'Copy FEN':
                    self.copyFEN()
        return False

    def noTimeLimit(self) -> None:
        'Sets up game to work without time limit'
        self.no_time_limit = True
        self.ui.player1_time.hide()
        self.ui.player2_time.hide()

    def pawnPromoteRequest(self, piecename) -> None:
        pawninfo = self.pawn_promote.pieceInformation()
        self.pawn_promote.setPieceInformation(piecename, pawninfo[1], pawninfo[2])
        if self.blindfold is False:
            self.pawn_promote.pieceShow()
        self.ui.pawnPromotion(pawninfo[2])
        if self.mutesound is False:
            self.s_promote.play()
        # Game state checks
        flip = {'white': 'black', 'black': 'white'}
        possiblechecks = self.calculateValidSquares(self.pawn_promote)
        oppositeking = flip[pawninfo[1]]
        if self.check is True:
            self.check_tile[0].setDefaultColor(self.check_tile[1])
            self.check_tile[0].resetColor()
            self.check = False
        if self.kingpos[oppositeking] in possiblechecks:
            self.check = True
            self.checkFunc(flip[pawninfo[1]])
        else:
            # Discovered check
            for i in range(64):
                widget = self.ui.piece_layout.itemAt(i).widget()
                widgetinfo = widget.pieceInformation()
                if widgetinfo[0] is None:
                    continue
                if widgetinfo[1] == pawninfo[1]:
                    checksquares = self.calculateValidSquares(widget)
                    if self.kingpos[oppositeking] in checksquares:
                        self.check = True
                        self.checkFunc(flip[widgetinfo[1]])
                        print(flip[widgetinfo[1]])
                        break
                else:
                    continue
        
        # Add to move log
        ref = {'rook': 'R', 'bishop': 'B', 'queen': 'Q', 'knight': 'N'}
        self.current_notation += '/' + ref[piecename]
        if pawninfo[1] == 'white':
            self.current_log.append(self.current_notation)
            self.move_log_pointer += 1
            self.move_log[self.move_log_pointer] = self.current_log[0]
            self.updateMoveLog(False)
        else:
            self.current_log.append(self.current_notation)
            self.move_log[self.move_log_pointer] = (self.current_log[0], self.current_log[1])
            self.current_log = []
            self.updateMoveLog(True)

        self.occupied = False
        self.promotion = True
        self.pawn_promote = None
        self.will_promote = False
        self.insufficientMaterialCheck()

        if pawninfo[1] == self.player1_color:
            self.engineactive = True
            self.engine_thread = EngineThread(self)
            self.engine_thread.finished.connect(self.engineMoveRequest)
            self.engine_thread.start()
        
        if not self.firstmove:
            self.timeController()
            self.firstmove = True
        self.timeSwitch()

    def returnKingPosition(self) -> dict:
        x = self.kingpos
        return x

    def engineMove(self) -> None:
        'Engine\'s turn to move.'
        self.parent.updateEngineFen(self.exportFEN())
        movetomake = self.parent.requestEngineMove()

        # Find piece and target info
        pos = self.convertSquareNotation(movetomake[0] + movetomake[1])
        pos = self.convertToPieceLayoutPos(pos)
        piece = self.ui.piece_layout.itemAtPosition(pos[0], pos[1]).widget()
        pos = self.convertSquareNotation(movetomake[2] + movetomake[3])
        pos = self.convertToPieceLayoutPos(pos)
        target = self.ui.piece_layout.itemAtPosition(pos[0], pos[1]).widget()

        # Make move
        self.enginereq = (piece, target)
        #self.movePiece(piece, target, True)
        
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

        # Clear board
        for i in range(64):
            widget = self.ui.piece_layout.itemAt(i).widget()
            widgetinfo = widget.pieceInformation()
            widget.setPieceInformation(None, None, widgetinfo[2])

        # Process piece placement data
        piece_ref = {'p': 'pawn', 'r': 'rook', 'b': 'bishop',
                     'n': 'knight','k': 'king', 'q': 'queen'}
        flip_digits = {1: 8, 2: 7, 3: 6, 4: 5,
                       5: 4, 6: 3, 7: 2, 8: 1}
        
        pieces = list(self.piece_placement)
        rank = 1
        file = 1
        for piece in pieces:
            if piece == '/':
                rank += 1
                file = 1
            elif piece.isnumeric():
                file += int(piece)
            elif piece.lower() in piece_ref:
                pos = self.convertToPieceLayoutPos((file, flip_digits[rank]))
                tilepos = self.convertSquareNotation((file, flip_digits[rank]))
                if piece.isupper():
                    self.placePiece(piece_ref[piece.lower()], 'white', pos, tilepos)
                else:
                    self.placePiece(piece_ref[piece], 'black', pos, tilepos)
                file += 1

    # Algebraic notation
    def algebraicNotation(self, piece, targetpos: str, capture: bool, check: bool, castle: str) -> str:
        '''Returns algebraic notation of piece if it were to move to targetpos, or returns notation of
        appropriate game conditions'''
        ref = {'knight': 'N', 'rook': 'R', 'king': 'K', 'queen': 'Q', 'bishop': 'B'}
        pieceinfo = piece.pieceInformation()

        # Identifying disambiguation
        identifier = ''
        need_to_disambiguate = []
        for i in range(64):
            widget = self.ui.piece_layout.itemAt(i).widget()
            if widget == piece:
                continue
            widgetinfo = widget.pieceInformation()
            if (widgetinfo[0] == pieceinfo[0]) and (widgetinfo[1] == pieceinfo[1]):
                valid = self.calculateValidMoves(widget)
                if targetpos in valid:
                    need_to_disambiguate.append(widget)
        if need_to_disambiguate:
            for piece_2 in need_to_disambiguate:
                pieceinfo_2 = piece_2.pieceInformation()
                if identifier == '':
                    if pieceinfo_2[2][0] == pieceinfo[2][0]:
                        if pieceinfo_2[2][1] == pieceinfo[2][1]:
                            identifier = pieceinfo[2]
                            break
                        else:
                            identifier = pieceinfo[2][1]
                    else:
                        identifier = pieceinfo[2][0]
                elif identifier.isalnum():
                    if pieceinfo_2[2][1] == identifier:
                        identifier = pieceinfo[2]
                        break
                else:
                    if pieceinfo_2[2][0] == identifier:
                        if pieceinfo_2[2][1] == pieceinfo[2][1]:
                            identifier = pieceinfo[2]
                            break
                        else:
                            identifier = pieceinfo[2][1]
            

        notation: str = targetpos
        if capture:
            notation = 'x' + notation
        if pieceinfo[0] != 'pawn':
            notation = ref[pieceinfo[0]] + identifier + notation
        else:
            notation = identifier + notation
        return notation

    def saveBoardPosition(self) -> list:
        'Provides a way to save and compare board positions for repetition rules'
        board_position = []
        for i in range(64):
            widget = self.ui.piece_layout.itemAt(i).widget()
            widgetinfo = widget.pieceInformation()
            board_position.append(widgetinfo)
        return board_position

    def threefoldRepetition(self) -> None:
        'Checks for threefold repetition by managing the stack of the last three moves'
        self.board_position_history.append(self.saveBoardPosition())

        # Threefold repetition check
        for position in self.board_position_history:
            if self.board_position_history.count(position) == 3:
                self.occupied = True
                self.parent.completeANIIL()
                self.s_end.play()
                self.timer1.stop()
                self.timer2.stop()
                self.ui.player1_time.setStyleSheet('color: #FFFFFF')
                self.ui.player1_label.setStyleSheet('color: #FFFFFF')
                self.ui.player2_time.setStyleSheet('color: #FFFFFF')
                self.ui.player2_label.setStyleSheet('color: #FFFFFF')
                self.ui.repetition()

    def enginePawnPromotion(self, pawn) -> None:
        'Promotes engine pawn to queen.'
        self.occupied = True
        self.pawn_promote = pawn
        pawninfo = self.pawn_promote.pieceInformation()
        self.pawn_promote.setPieceInformation('queen', pawninfo[1], pawninfo[2])
        if self.blindfold is False:
            self.pawn_promote.pieceShow()
        if self.mutesound is False:
            self.s_promote.play()
        # Game state checks
        flip = {'white': 'black', 'black': 'white'}
        possiblechecks = self.calculateValidSquares(self.pawn_promote)
        oppositeking = flip[pawninfo[1]]
        if self.check is True:
            self.check_tile[0].setDefaultColor(self.check_tile[1])
            self.check_tile[0].resetColor()
            self.check = False
        if self.kingpos[oppositeking] in possiblechecks:
            self.check = True
            self.checkFunc(flip[pawninfo[1]])
        else:
            # Discovered check
            for i in range(64):
                widget = self.ui.piece_layout.itemAt(i).widget()
                widgetinfo = widget.pieceInformation()
                if widgetinfo[0] is None:
                    continue
                if widgetinfo[1] == pawninfo[1]:
                    checksquares = self.calculateValidSquares(widget)
                    if self.kingpos[oppositeking] in checksquares:
                        self.check = True
                        self.checkFunc(flip[widgetinfo[1]])
                        print(flip[widgetinfo[1]])
                        break
                else:
                    continue
        
        # Add to move log
        self.current_notation += '/' + 'Q'
        if pawninfo[1] == 'white':
            self.current_log.append(self.current_notation)
            self.move_log_pointer += 1
            self.move_log[self.move_log_pointer] = self.current_log[0]
            self.updateMoveLog(False)
        else:
            self.current_log.append(self.current_notation)
            self.move_log[self.move_log_pointer] = (self.current_log[0], self.current_log[1])
            self.current_log = []
            self.updateMoveLog(True)

        self.occupied = False
        self.promotion = True
        self.pawn_promote = None
        self.will_promote = False
        self.insufficientMaterialCheck()

    # Returns new FEN string
    def exportFEN(self) -> str:
        sections = []

        # Section 1
        piece_ref = {'pawn': 'p', 'rook': 'r', 'bishop': 'b',
                     'knight': 'n','king': 'k', 'queen': 'q'}
        section = []
        empty = 0
        for r in '87654321':
            for f in 'abcdefgh':
                position = self.convertSquareNotation(f+r)
                position = self.convertToPieceLayoutPos(position)
                piece = self.ui.piece_layout.itemAtPosition(position[0], position[1]).widget()
                pieceinfo = piece.pieceInformation()
                if pieceinfo[0] is not None:
                    if empty:
                        section.append(str(empty))
                        empty = 0
                    if pieceinfo[1] == 'white':
                        section.append(piece_ref[pieceinfo[0]].upper())
                    else:
                        section.append(piece_ref[pieceinfo[0]])
                else:
                    empty += 1
            if empty:
                section.append(str(empty))
                empty = 0
            if r != '1':
                section.append('/')
        sections.append(''.join(section))

        # Section 2
        sections.append(self.active_color)

        # Section 3
        castling_availability = ''
        whiteking = self.ui.piece_layout.itemAtPosition(7, 4).widget()
        blackking = self.ui.piece_layout.itemAtPosition(0, 4).widget()
        whitekinginfo = whiteking.pieceInformation()
        blackkinginfo = blackking.pieceInformation()
        kwhiterook = self.ui.piece_layout.itemAtPosition(7, 7).widget()
        qwhiterook = self.ui.piece_layout.itemAtPosition(7, 0).widget()
        kblackrook = self.ui.piece_layout.itemAtPosition(0, 7).widget()
        qblackrook = self.ui.piece_layout.itemAtPosition(0, 0).widget()
        kwhiterookinfo = kwhiterook.pieceInformation()
        qwhiterookinfo = kwhiterook.pieceInformation()
        kblackrookinfo = kblackrook.pieceInformation()
        qblackrookinfo = qblackrook.pieceInformation()

        if (whitekinginfo[0] == 'king') and (whitekinginfo[1] == 'white') and (whiteking.moved is False):
            if (kwhiterookinfo[0] == 'rook') and (kwhiterookinfo[1] == 'white') and (kwhiterook.moved is False):
                castling_availability += 'K'
            if (qwhiterookinfo[0] == 'rook') and (qwhiterookinfo[1] == 'white') and (qwhiterook.moved is False):
                castling_availability += 'Q'
        if (blackkinginfo[0] == 'king') and (blackkinginfo[1] == 'black') and (blackking.moved is False):
            if (kblackrookinfo[0] == 'rook') and (kblackrookinfo[1] == 'black') and (kblackrook.moved is False):
                castling_availability += 'k'
            if (qblackrookinfo[0] == 'rook') and (qblackrookinfo[1] == 'black') and (qblackrook.moved is False):
                castling_availability += 'q'
        
        if castling_availability == '':
            sections.append('-')
        else:
            sections.append(castling_availability)

        # Section 4
        sections.append(self.enpassant_square)

        # Section 5
        sections.append(self.halfmove_clock)

        # Section 6
        sections.append(self.fullmove_clock)

        newfen = f'{sections[0]} {sections[1]} {sections[2]} {sections[3]} {sections[4]} {sections[5]}'
        return newfen

    # Copies FEN string to system clipboard
    def copyFEN(self) -> None:
        fen = self.exportFEN()
        clipboard = QApplication.clipboard()
        clipboard.setText(fen)
        event = QEvent(QEvent.Clipboard)
        self.parent.application.sendEvent(clipboard, event)

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
        if not self.no_time_limit and self.clock1_active:
            self.clock1 -= 1
            self.ui.player1_time.setText(self.convertTime(self.clock1))

            if self.clock1 == 0:
                self.timer1.stop()
                self.occupied = True
                self.timeloss(self.player1_color)
                self.ui.player1_time.setStyleSheet('color: #FF4848')
                self.ui.player1_label.setStyleSheet('color: #FFFFFF')
                self.ui.player2_time.setStyleSheet('color: #FFFFFF')
                self.ui.player2_label.setStyleSheet('color: #FFFFFF')

    # Updates timer 2 for timeController
    def update2(self):
        if not self.no_time_limit and self.clock2_active:
            self.clock2 -= 1
            self.ui.player2_time.setText(self.convertTime(self.clock2))

            if self.clock2 == 0:
                self.timer2.stop()
                self.occupied = True
                self.timeloss(self.player1_color)
                self.ui.player2_time.setStyleSheet('color: #FF4848')
                self.ui.player2_label.setStyleSheet('color: #FFFFFF')
                self.ui.player1_time.setStyleSheet('color: #FFFFFF')
                self.ui.player1_label.setStyleSheet('color: #FFFFFF')

    # Controls the countdown and functionality of the timers
    def timeController(self) -> None:
        self.timer1 = QTimer()
        self.timer2 = QTimer()
        self.timer1.timeout.connect(self.update1)
        self.timer2.timeout.connect(self.update2)
        if not self.firstmove:
            if self.active_color == 'b':
                # Switch to black
                if not self.no_time_limit:
                    self.timer2.start(1000)
                self.clock2_active = True
                self.ui.player2_label.setStyleSheet('color: #FFFFFF')
                self.ui.player2_time.setStyleSheet('color: #FFFFFF')
                self.ui.player1_label.setStyleSheet('color: #404040')
                self.ui.player1_time.setStyleSheet('color: #404040')
            else:
                # Switch to white
                if not self.no_time_limit:
                    self.timer1.start(1000)
                self.clock1_active = True
                self.ui.player1_label.setStyleSheet('color: #FFFFFF')
                self.ui.player1_time.setStyleSheet('color: #FFFFFF')
                self.ui.player2_label.setStyleSheet('color: #404040')
                self.ui.player2_time.setStyleSheet('color: #404040')

    # Switches timers
    def timeSwitch(self) -> None:
        if self.occupied:
            return
        if self.clock1_active:
            if not self.no_time_limit:
                self.timer1.stop()
                self.timer2.start(1000)
                self.clock1 += 1
                self.ui.player1_time.setText(self.convertTime(self.clock1))
                self.parent.current_data_file.setTiming(1, self.clock1)
            self.clock1_active = False
            self.clock2_active = True
            self.ui.player2_label.setStyleSheet('color: #FFFFFF')
            self.ui.player2_time.setStyleSheet('color: #FFFFFF')
            self.ui.player1_label.setStyleSheet('color: #404040')
            self.ui.player1_time.setStyleSheet('color: #404040')
        elif self.clock2_active:
            if not self.no_time_limit:
                self.timer2.stop()
                self.timer1.start(1000)
                self.clock2 += 1
                self.ui.player2_time.setText(self.convertTime(self.clock2))
                self.parent.current_data_file.setTiming(2, self.clock2)
            self.clock1_active = True
            self.clock2_active = False
            self.ui.player1_label.setStyleSheet('color: #FFFFFF')
            self.ui.player1_time.setStyleSheet('color: #FFFFFF')
            self.ui.player2_label.setStyleSheet('color: #404040')
            self.ui.player2_time.setStyleSheet('color: #404040')
        return

    # Executes upon mouse click
    def mousePressEvent(self, event: QKeyEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.occupied:
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
        if self.occupied or self.engineactive:
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
                movepiece = self.movePiece(self.active_piece, piece, False)
                if movepiece:
                    self.second_active = tile
                    if not self.hide_highlights:
                        self.second_active.setStyleSheet(f'background-color: {self.highlight}')
                        self.active_tile.setStyleSheet(f'background-color: {self.highlight2}')

                        # Engine move
                        if not self.will_promote:
                            self.engineactive = True
                            self.engine_thread = EngineThread(self)
                            self.engine_thread.finished.connect(self.engineMoveRequest)
                            self.engine_thread.start()
                else:
                    self.hideHints()
                    self.active_tile.resetColor()
                    self.active_tile = None
                    self.active_piece = None
        # Deselect tiles
        else:
            self.hideHints()
            self.active_tile.resetColor()
            self.active_tile = None
            self.active_piece = None

    def engineMoveRequest(self):
        'Executes engine move.'
        self.hideHints()
        if self.active_tile is not None:
            self.active_tile.resetColor()
        if self.second_active is not None:
            self.second_active.resetColor()
        self.second_active = None
        self.active_tile = None
        self.active_piece = None

        self.movePiece(self.enginereq[0],self.enginereq[1], False)
        self.parent.updateEngineFen(self.exportFEN())
        self.engineactive = False

        # Engine move highlights
        pos1 = self.enginereq[0].pieceInformation()
        pos1 = self.convertSquareNotation(pos1[2])
        pos1 = self.convertToPieceLayoutPos(pos1)
        pos2 = self.enginereq[1].pieceInformation()
        pos2 = self.convertSquareNotation(pos2[2])
        pos2 = self.convertToPieceLayoutPos(pos2)
        self.second_active = self.ui.board_layout.itemAtPosition(pos2[0], pos2[1]).widget()
        self.active_tile = self.ui.board_layout.itemAtPosition(pos1[0], pos1[1]).widget()
        if not self.hide_highlights:
            self.second_active.setStyleSheet(f'background-color: {self.highlight}')
            self.active_tile.setStyleSheet(f'background-color: {self.highlight2}')

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

        # Checkmate code
        for i in range(64):
            piece = self.ui.piece_layout.itemAt(i).widget()
            valid = self.calculateValidMoves(piece)
            pieceinfo = piece.pieceInformation()
            if pieceinfo[1] != kingcolor:
                continue
            if self.returnHints(valid, piece):
                self.current_notation += '+'
                return
        self.checkmate(kingcolor)
        self.current_notation += '#'

    def checkmate(self, color):
        'Function called when color is checkmated'
        flip = {'white': 'black', 'black': 'white'}
        self.occupied = True
        self.s_end.play()
        if not self.no_time_limit:
            self.timer1.stop()
            self.timer2.stop()
        self.ui.player1_time.setStyleSheet('color: #FFFFFF')
        self.ui.player1_label.setStyleSheet('color: #FFFFFF')
        self.ui.player2_time.setStyleSheet('color: #FFFFFF')
        self.ui.player2_label.setStyleSheet('color: #FFFFFF')
        self.ui.checkmate(flip[color])
        self.is_checkmate = True
        self.parent.completeANIIL()
    
    def timeloss(self, color):
        'Function called when color loses on time'
        flip = {'white': 'black', 'black': 'white'}
        self.occupied = True
        self.s_end.play()
        if not self.no_time_limit:
            self.timer1.stop()
            self.timer2.stop()
        self.ui.timeloss(flip[color])
        if color == 'white':
            self.current_log.append('0-1')
            self.move_log_pointer += 1
            self.move_log[self.move_log_pointer] = self.current_log[0]
            self.updateMoveLog(False)
        else:
            self.current_log.append('1-0')
            self.move_log[self.move_log_pointer] = (self.current_log[0], self.current_log[1])
            self.current_log = []
            self.updateMoveLog(True)
        self.parent.completeANIIL()

    def stalemate(self):
        'Function to execute when there is a stalemate'
        self.occupied = True
        self.s_end.play()
        if not self.no_time_limit:
            self.timer1.stop()
            self.timer2.stop()
        self.ui.player1_time.setStyleSheet('color: #FFFFFF')
        self.ui.player1_label.setStyleSheet('color: #FFFFFF')
        self.ui.player2_time.setStyleSheet('color: #FFFFFF')
        self.ui.player2_label.setStyleSheet('color: #FFFFFF')
        self.ui.stalemate()
        if self.active_color == 'w':
            self.current_log.append('==')
            self.move_log_pointer += 1
            self.move_log[self.move_log_pointer] = self.current_log[0]
            self.updateMoveLog(False)
        else:
            self.current_log.append('==')
            self.move_log[self.move_log_pointer] = (self.current_log[0], self.current_log[1])
            self.current_log = []
            self.updateMoveLog(True)
        self.parent.completeANIIL()

    def fiftymove(self) -> None:
        'Function to execute when there is a draw via fifty-move rule'
        self.occupied = True
        self.s_end.play()
        if not self.no_time_limit:
            self.timer1.stop()
            self.timer2.stop()
        self.ui.player1_time.setStyleSheet('color: #FFFFFF')
        self.ui.player1_label.setStyleSheet('color: #FFFFFF')
        self.ui.player2_time.setStyleSheet('color: #FFFFFF')
        self.ui.player2_label.setStyleSheet('color: #FFFFFF')
        self.ui.fiftymove()
        if self.active_color == 'w':
            self.current_log.append('==')
            self.move_log_pointer += 1
            self.move_log[self.move_log_pointer] = self.current_log[0]
            self.updateMoveLog(False)
        else:
            self.current_log.append('==')
            self.move_log[self.move_log_pointer] = (self.current_log[0], self.current_log[1])
            self.current_log = []
            self.updateMoveLog(True)
        self.parent.completeANIIL()

    def insufficientMaterialCheck(self) -> None:
        'Checks to see if a draw can be called due to insufficient material on the board'
        all_pieces = []
        all_pieces_withdata = []
        for i in range(64):
            piece = self.ui.piece_layout.itemAt(i).widget()
            pieceinfo = piece.pieceInformation()
            if pieceinfo[0] is not None:
                all_pieces.append(pieceinfo[0])
                all_pieces_withdata.append(pieceinfo)
        
        # King versus king
        if len(all_pieces) == 2:
            self.insufficientMaterial()
        # King and knight versus king
        elif (len(all_pieces) == 3) and ('knight' in all_pieces):
            self.insufficientMaterial()
        # King and bishop versus king
        elif (len(all_pieces) == 3) and ('bishop' in all_pieces):
            self.insufficientMaterial()
        # King a bishop versus a king and a bishop, with bishops of the same color
        elif (len(all_pieces) == 4) and (all_pieces.count('bishop') == 2):
            light_tiles = []
            for row, rank in enumerate('12345678'):
                for col, file in enumerate('abcdefgh'):
                    if row % 2 == col % 2:
                        light_tiles.append(file+rank)

            bishops = []
            for i, piece in enumerate(all_pieces):
                if piece == 'bishop':
                    bishops.append(all_pieces_withdata[i])
            if (bishops[0][1] != bishops[1][1]):
                if (bishops[0][2] in light_tiles) and (bishops[1][2] in light_tiles):
                    self.insufficientMaterial()
                elif (bishops[0][2] not in light_tiles) and (bishops[1][2] not in light_tiles):
                    self.insufficientMaterial()
        
    def insufficientMaterial(self) -> None:
        'Function to execute when there is a draw via insufficient material'
        self.occupied = True
        self.s_end.play()
        if not self.no_time_limit:
            self.timer1.stop()
            self.timer2.stop()
        self.ui.player1_time.setStyleSheet('color: #FFFFFF')
        self.ui.player1_label.setStyleSheet('color: #FFFFFF')
        self.ui.player2_time.setStyleSheet('color: #FFFFFF')
        self.ui.player2_label.setStyleSheet('color: #FFFFFF')
        self.ui.insufficientMaterial()
        if self.active_color == 'w':
            self.current_log.append('==')
            self.move_log_pointer += 1
            self.move_log[self.move_log_pointer] = self.current_log[0]
            self.updateMoveLog(False)
        else:
            self.current_log.append('==')
            self.move_log[self.move_log_pointer] = (self.current_log[0], self.current_log[1])
            self.current_log = []
            self.updateMoveLog(True)
        self.parent.completeANIIL()

    # Moves piece
    def movePiece(self, piece, target, enginereq: bool) -> None:
        'Sets target piece data to the piece that just captured /  moved.'
        flip = {'white': 'black', 'black': 'white'}
        pieceinfo = piece.pieceInformation()
        targetinfo = target.pieceInformation()
        valid = self.calculateValidMoves(piece)
        if targetinfo[2] in valid:
            # Half-move and full-move clocks
            if (pieceinfo[0] == 'pawn') or (targetinfo[0] is not None):
                self.halfmove_clock = 0
            else:
                self.halfmove_clock += 1
            if pieceinfo[1] == 'black':
                self.fullmove_clock += 1

            # Sound
            if self.mutesound is False:
                if targetinfo[0] is None:
                    self.s_move.play()
                    capture = False
                else:
                    self.ui.capturePiece(targetinfo[1], targetinfo[0])
                    self.s_capture.play()
                    capture = True
            self.hideHints()
            self.current_notation = self.algebraicNotation(piece, targetinfo[2], capture, False, False)

            # Castle check
            if (pieceinfo[0] == 'king') and (targetinfo[2] in piece.castlemoves):
                # white kingside
                if pieceinfo[1] == 'white' and targetinfo[2] == 'g1':
                    target2 = self.ui.piece_layout.itemAtPosition(7, 7).widget()
                    target2.setPieceInformation(None, None, 'h1')
                    if self.blindfold is False:
                        target2.pieceShow()
                    target2 = self.ui.piece_layout.itemAtPosition(7, 5).widget()
                    target2.setPieceInformation('rook', 'white', 'f1')
                    if self.blindfold is False:
                        target2.pieceShow()
                    if self.active_tile is not None:
                        self.active_tile.resetColor()
                        self.active_tile = self.ui.board_layout.itemAtPosition(7, 5).widget()
                    self.current_notation = 'O-O'
                # white queenside
                elif pieceinfo[1] == 'white' and targetinfo[2] == 'c1':
                    target2 = self.ui.piece_layout.itemAtPosition(7, 0).widget()
                    target2.setPieceInformation(None, None, 'a1')
                    if self.blindfold is False:
                        target2.pieceShow()
                    target2 = self.ui.piece_layout.itemAtPosition(7, 3).widget()
                    target2.setPieceInformation('rook', 'white', 'd1')
                    if self.blindfold is False:
                        target2.pieceShow()
                    if self.active_tile is not None:
                        self.active_tile.resetColor()
                        self.active_tile = self.ui.board_layout.itemAtPosition(7, 3).widget()
                    self.current_notation = 'O-O-O'
                # black kingside
                elif pieceinfo[1] == 'black' and targetinfo[2] == 'g8':
                    target2 = self.ui.piece_layout.itemAtPosition(0, 7).widget()
                    target2.setPieceInformation(None, None, 'h8')
                    if self.blindfold is False:
                        target2.pieceShow()
                    target2 = self.ui.piece_layout.itemAtPosition(0, 5).widget()
                    target2.setPieceInformation('rook', 'black', 'f8')
                    if self.blindfold is False:
                        target2.pieceShow()
                    if self.active_tile is not None:
                        self.active_tile.resetColor()
                        self.active_tile = self.ui.board_layout.itemAtPosition(0, 5).widget()
                    self.current_notation = 'O-O'
                # black queenside
                elif pieceinfo[1] == 'black' and targetinfo[2] == 'c8':
                    target2 = self.ui.piece_layout.itemAtPosition(0, 0).widget()
                    target2.setPieceInformation(None, None, 'a8')
                    if self.blindfold is False:
                        target2.pieceShow()
                    target2 = self.ui.piece_layout.itemAtPosition(0, 3).widget()
                    target2.setPieceInformation('rook', 'black', 'd8')
                    if self.blindfold is False:
                        target2.pieceShow()
                    if self.active_tile is not None:
                        self.active_tile.resetColor()
                        self.active_tile = self.ui.board_layout.itemAtPosition(0, 3).widget()
                    self.current_notation = 'O-O-O'
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
                    captureinfo = capturepiece.pieceInformation()
                    self.ui.capturePiece(captureinfo[1], captureinfo[0])
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
                    if self.gametype == 'engine':
                        if self.player1_color == 'white':
                            self.showPawnPromotion(target, 'white')
                            self.will_promote = True
                        else:
                            self.enginePawnPromotion(target)
                            self.enginedidpromote = True
                    else:
                        self.showPawnPromotion(target, 'white')
                        self.will_promote = True
                elif (targetinfo[1] == 'black') and (pawnrank == 1):
                    if self.gametype == 'engine':
                        if self.player1_color == 'black':
                            self.showPawnPromotion(target, 'black')
                            self.will_promote = True
                        else:
                            self.enginePawnPromotion(target)
                            self.enginedidpromote = True
                    else:
                        self.showPawnPromotion(target, 'black')
                        self.will_promote = True

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
                #self.player1_color = 'black'
                self.active_color = 'b'
            else:
                #self.player1_color = 'white'
                self.active_color = 'w'
            self.stalemateCheck()

            log_to_write = None
            if self.will_promote is False and self.enginedidpromote is False:
                if targetinfo[1] == 'white':
                    self.current_log.append(self.current_notation)
                    self.move_log_pointer += 1
                    self.move_log[self.move_log_pointer] = self.current_log[0]
                    self.updateMoveLog(False)
                else:
                    self.current_log.append(self.current_notation)
                    self.move_log[self.move_log_pointer] = (self.current_log[0], self.current_log[1])
                    log_to_write = f'{self.current_log[0]}/{self.current_log[1]}'
                    self.current_log = []
                    self.updateMoveLog(True)

            self.threefoldRepetition()
            if self.halfmove_clock == 50:
                self.fiftymove()
            self.insufficientMaterialCheck()
            self.enginedidpromote = False

            # Save to aniil
            self.parent.current_data_file.updateFEN(self.exportFEN())
            if log_to_write is not None:
                self.parent.current_data_file.writeLog(log_to_write)

            # First move
            if not enginereq:
                if not self.firstmove:
                    self.timeController()
                    self.firstmove = True
                    return True
                self.timeSwitch()
                return True
        else:
            return False

    def stalemateCheck(self) -> None:
        'Function to check whether there is a stalemate.'
        if self.is_checkmate:
            return
        whitepieces = []
        blackpieces = []
        for i in range(64):
            piece = self.ui.piece_layout.itemAt(i).widget()
            pieceinfo = piece.pieceInformation()
            if pieceinfo[1] == 'white':
                whitepieces.append(piece)
            elif pieceinfo[1] == 'black':
                blackpieces.append(piece)

        # Check for white stalemate
        valid = []
        for piece in whitepieces:
            tempvalid = self.calculateValidMoves(piece)
            pieceinfo = piece.pieceInformation()
            for temp in tempvalid:
                pos = self.convertSquareNotation(temp)
                pos = self.convertToPieceLayoutPos(pos)
                widget = self.ui.piece_layout.itemAtPosition(pos[0], pos[1]).widget()
                widgetinfo = widget.pieceInformation()
                if widgetinfo[1] != pieceinfo[1]:
                    valid.append(temp)
        if valid:
            pass
        else:
            self.stalemate()


        # Check for black stalemate
        valid = []
        for piece in blackpieces:
            tempvalid = self.calculateValidMoves(piece)
            pieceinfo = piece.pieceInformation()
            for temp in tempvalid:
                pos = self.convertSquareNotation(temp)
                pos = self.convertToPieceLayoutPos(pos)
                widget = self.ui.piece_layout.itemAtPosition(pos[0], pos[1]).widget()
                widgetinfo = widget.pieceInformation()
                if widgetinfo[1] != pieceinfo[1]:
                    valid.append(temp)
        if valid:
            pass
        else:
            self.stalemate()
        return

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

    def returnHints(self, validmoves: list, piece) -> list:
        hints = []
        if self.hidehints is False:
            for valid in validmoves:
                pos = self.convertSquareNotation(valid)
                pos = self.convertToPieceLayoutPos(pos)
                widget = self.ui.piece_layout.itemAtPosition(pos[0], pos[1]).widget()
                widget2 = self.ui.hint_layout.itemAtPosition(pos[0], pos[1]).widget()
                pieceinfo = piece.pieceInformation()
                widgetinfo = widget.pieceInformation()
                if widget.name is None:
                    a = True
                else:
                    a = False
                if a:
                    hints.append(widget)
                elif pieceinfo[1] != widgetinfo[1]:
                    hints.append(widget2)
        return hints

    def hideHints(self) -> None:
        'Method to hide all hints on the board'
        for hint in self.hints:
            hint.removeHint()
        self.hints = []

    def updateMoveLog(self, full: bool) -> None:
        'Updates move log'
        log_index = self.move_log_pointer
        if full:
            log_line = f'{log_index}.   {self.move_log[log_index][0]} {self.move_log[log_index][1]}'
            self.ui.updateMoveLog(log_line, True)
        else:
            log_line = f'{log_index}.   {self.move_log[log_index]}'
            self.ui.updateMoveLog(log_line, False)

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

            if (not self.checkObstruction(two_up)) and (not self.checkObstruction(up)):
                if (pieceinfo[1] == 'white') and (int(pieceinfo[2][1]) == 2):
                    tempvalid.append(two_up)
                elif (pieceinfo[1] == 'black') and (int(pieceinfo[2][1]) == 7):
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

            for i in range(1, 8):
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

            for i in range(1, 8):
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
                    temppos = self.convertToPieceLayoutPos(square)
                    widget = self.ui.piece_layout.itemAtPosition(temppos[0], temppos[1]).widget()
                    widgetinfo = widget.pieceInformation()
                    if widgetinfo[1] != pieceinfo[1]:
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

    def resignRequest(self) -> None:
        'Function executed when user resigns'
        self.occupied = True
        self.s_end.play()
        if not self.no_time_limit:
            self.timer1.stop()
            self.timer2.stop()
        self.ui.player1_time.setStyleSheet('color: #FFFFFF')
        self.ui.player1_label.setStyleSheet('color: #FFFFFF')
        self.ui.player2_time.setStyleSheet('color: #FFFFFF')
        self.ui.player2_label.setStyleSheet('color: #FFFFFF')
        if self.active_color == 'w':
            self.ui.resign('white')
            self.current_log.append('0-1')
            self.move_log_pointer += 1
            self.move_log[self.move_log_pointer] = self.current_log[0]
            self.updateMoveLog(False)
        else:
            self.ui.resign('black')
            self.current_log.append('1-0')
            self.move_log[self.move_log_pointer] = (self.current_log[0], self.current_log[1])
            self.current_log = []
            self.updateMoveLog(True)
        self.is_checkmate = True
        self.parent.completeANIIL()

    def drawRequest(self) -> None:
        'Function executed when user requests to draw'
        self.occupied = True
        self.s_end.play()
        if not self.no_time_limit:
            self.timer1.stop()
            self.timer2.stop()
        self.ui.player1_time.setStyleSheet('color: #FFFFFF')
        self.ui.player1_label.setStyleSheet('color: #FFFFFF')
        self.ui.player2_time.setStyleSheet('color: #FFFFFF')
        self.ui.player2_label.setStyleSheet('color: #FFFFFF')
        self.ui.draw()
        if self.active_color == 'w':
            self.current_log.append('==')
            self.move_log_pointer += 1
            self.move_log[self.move_log_pointer] = self.current_log[0]
            self.updateMoveLog(False)
        else:
            self.current_log.append('==')
            self.move_log[self.move_log_pointer] = (self.current_log[0], self.current_log[1])
            self.current_log = []
            self.updateMoveLog(True)
        self.parent.completeANIIL()


class ConfirmWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.ui = chessboardui.UI_ConfirmWindow()
        self.confirmation = 0

        self.render()

    # Render UI elements for the window
    def render(self) -> None:
        self.ui.initUI(self)
        self.setFixedSize(318, 145)
        self.setWindowTitle('Confirm')

        self.ui.yes_button.clicked.connect(self.processYes)
        self.ui.no_button.clicked.connect(self.processNo)

    def closeWindow(self) -> None:
        self.close()
        self.parent.parent.setCurrentSubwindow(0)

    # Override close event when window is manually closed
    def closeEvent(self, event: QCloseEvent):
        self.parent.windowstack.pop()
        return super().closeEvent(event)
    
    def setConfirmation(self, conf) -> None:
        self.confirmation = conf
        if self.confirmation == 0:
            self.ui.heading.setText('Save game before exiting?')
        if self.confirmation == 1:
            self.ui.heading.setText('Resign from current game?')
        if self.confirmation == 2:
            self.ui.heading.setText('Draw the current game?')

    def processYes(self) -> None:
        if self.confirmation == 0:
            self.closeWindow()
        elif self.confirmation == 1:
            self.parent.resignRequest()
            self.close()
        elif self.confirmation == 2:
            self.parent.drawRequest()
            self.close()
    
    def processNo(self) -> None:
        if self.confirmation == 0:
            self.parent.parent.deleteANIIL()
            self.closeWindow()
        elif self.confirmation == 1:
            self.close()
        elif self.confirmation == 2:
            self.close()

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