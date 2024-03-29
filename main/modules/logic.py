# main/logic.py
# Processes all chess logic in raw form
from random import shuffle


class Board:
    def __init__(self, setter):
        self.board = self.emptyBoard()
        self.all_pieces: list = []
        self.fen = None
        self.position_history = []
        self.setBoard(setter)
        self.savePosition()
        self.checkmate = None
        self.stalemate = False
        self.draw = False
        self.last_move = None
        self.previous_enpassant_target = '-'

    # Public Get methods ///
    def getBoard(self) -> list:
        'Returns board array. (Getter)'
        return self.board.copy()
    def allPieces(self) -> list:
        'Returns all current pieces in an array. (Getter)'
        return self.all_pieces.copy()
    def getFen(self) -> str:
        'Returns current fen. (Getter)'
        return self.fen
    def pieceAt(self, pos):
        'Returns piece instance at position of either string or tuple. (Getter)'
        try:
            board = self.board.copy()
            if isinstance(pos, tuple):
                if str(pos[0]) not in '12345678':
                    return None
                if str(pos[1]) not in '12345678':
                    return None
                return board[pos[0]-1][pos[1]-1]
            elif isinstance(pos, str):
                pos_tuple = self.convertPosType(pos)
                if str(pos_tuple[0]) not in '12345678':
                    return None
                if str(pos_tuple[1]) not in '12345678':
                    return None
                return board[pos_tuple[0]-1][pos_tuple[1]-1]
        # Piece does not exist
        except:  # noqa: E722
            return None
    def currentPosition(self) -> list:
        position = self.emptyBoard()
        for file in range(8):
            for rank in range(8):
                if self.pieceAt((file, rank)) is not None:
                    position[file][rank] = self.pieceAt((file, rank)).data()
                else:
                    position[file][rank] = None
        return position.copy()
    def positionHistory(self) -> list:
        'Returns position history of the board. (Getter)'
        return self.position_history.copy()
    def checkState(self, color: str) -> bool:
        'Returns boolean whether the color is currently in check. (Getter)'
        for piece in self.all_pieces:
            valid_moves = piece.calculatePsuedoLegal()
            for move in valid_moves:
                if self.pieceAt(move) is not None:
                    if (self.pieceAt(move).getName() == 'king') and (self.pieceAt(move).getColor() == color):
                        return True
        return False
    def checkmateState(self, color: str) -> bool:
        'Returns whether color has been checkmated. (Getter)'
        if self.checkmate is not None:
            if self.checkmate == color:
                return True
        return False
    def stalemateState(self) -> bool:
        'Returns whether position is in stalemate. (Getter)'
        state = self.draw or self.stalemate
        return state
    def allPossibleMoves(self, color: str) -> list:
        'Returns array of tuples in the form (piece, move) for every possible move'
        possible_moves = []
        for piece in self.allPieces():
            if piece.getColor() == color:
                for move in piece.legalMoves():
                    copiedpiece = Piece(piece.getName(), piece.getColor(), piece.getPos(), piece.hasMoved(), self)
                    possible_moves.append((copiedpiece, move))
        shuffle(possible_moves)
        return possible_moves.copy()

    # Public Set methods ///
    def setBoard(self, setter):
        'Replaces board with parameter setter of fen string or board instance. (Setter)'
        if isinstance(setter, str):
            self.fen = FEN(setter)
            self.FenToBoard(self.fen)
        elif isinstance(setter, Board):
            self.copyBoard(setter)
            self.fen = FEN(setter)
    def setPiece(self, piece, target):
        'Sets piece at specified position on the board, replacing any existing piece. (Setter)'
        try:
            if isinstance(target, str):
                pos = self.convertPosType(target)
                self.board[pos[0]-1][pos[1]-1] = piece
            elif isinstance(target, tuple):
                self.board[target[0]-1][target[1]-1] = piece
            if piece is not None:
                piece.setPos(target)
            self.updateAllPieces()
        # Does not exist
        except:  # noqa: E722
            return
    def promote(self, piece):
        'Promotes pawn to the best possible piece. (Setter)'
        check = ['knight', 'bishop', 'rook']
        for name in check:
            piece.setName(name)
            self.updateAllPieces()
            if piece.color == 'white':
                if self.identifyCheckmate('black'):
                    return
            elif piece.color == 'black':
                if self.identifyCheckmate('white'):
                    return
        piece.setName('queen')
        self.updateAllPieces()

    # Other methods ///
    def FenToBoard(self, fen) -> None:
        'Imports fen string and sets board with specified position and variables.'
        self.active_color = fen.activeColor()
        self.castling_availability = fen.castlingAvailability()
        self.enpassant_target = fen.enpassantTargetSquare()
        self.halfmove_clock = fen.halfmoveClock()
        self.fullmove_clock = fen.fullmoveClock()

        # Pieces onto the board
        piece_ref = {'p': 'pawn', 'r': 'rook', 'b': 'bishop',
                     'n': 'knight','k': 'king', 'q': 'queen'}
        file = 1
        rank = 8
        placements = fen.piecePlacement()
        for placement in placements:
            if placement == '/':
                rank -= 1
                file = 1
            elif placement.isnumeric():
                file += int(placement)
            elif placement.lower() in piece_ref:
                if placement.isupper():
                    piece = Piece(piece_ref[placement.lower()], 'white', self.convertPosType((file, rank)), False, self)
                    self.board[file-1][rank-1] = piece
                else:
                    piece = Piece(piece_ref[placement], 'black', self.convertPosType((file, rank)), False, self)
                    self.board[file-1][rank-1] = piece
                file += 1
        self.updateAllPieces()
    def emptyBoard(self) -> list:
        'Returns an initial empty board.'
        board = [[], [], [], [], [], [], [], []]
        for file in range(8):
            for rank in range(8):
                board[file].append(None)
        return board
    def convertPosType(self, pos):
        'Converts position between string and tuple format, returns None if pos is invalid.'
        str_reference = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5,
                         'f': 6, 'g': 7, 'h': 8}
        try:
            # Convert str -> tuple
            if isinstance(pos, str):
                return (str_reference[pos[0]], int(pos[1]))
            # Convert tuple -> str
            elif isinstance(pos, tuple):
                int_reference = {v: k for k, v in str_reference.items()}
                return int_reference[pos[0]] + str(pos[1])
            else:
                # Invalid type
                return None
        # Pos values outside board boundaries, so invalid
        except ValueError:
            return None
    def savePosition(self) -> None:
        'Saves position and appends to position history.'
        self.position_history.append(self.currentPosition())
    def updateAllPieces(self) -> None:
        'Updates the contents of all pieces attribute.'
        all_pieces = []
        for f in range(8):
            for r in range(8):
                if self.pieceAt(self.convertPosType((f+1, r+1))) is not None:
                    piece = self.pieceAt(self.convertPosType((f+1, r+1)))
                    all_pieces.append(Piece(piece.getName(), piece.getColor(), piece.getPos(), piece.hasMoved(), self))
        self.all_pieces = all_pieces.copy()
    def identifyCheckmate(self, color: str) -> bool:
        'Private method to check whether color has been checkmated.'
        for piece in self.allPieces():
            if piece.getColor() == color:
                if piece.legalMoves():
                    return False
        if self.checkState(color):
            return True
        return False
    def identifyStalemate(self, colortomove: str) -> bool:
        'Private method to check for a stalemate.'
        for piece in self.allPieces():
            if piece.getColor() == colortomove:
                if piece.legalMoves():
                    return False
        return True
    def castlingChecks(self) -> None:
        'Function that updates castling availability.'
        castling = list(self.castling_availability)
        # White castling
        if self.pieceAt('e1') is None:
            if 'K' in castling:
                    castling.pop(castling.index('K'))
            if 'Q' in castling:
                castling.pop(castling.index('Q'))
        elif self.pieceAt('e1').name != 'king':
            if 'K' in castling:
                castling.pop(castling.index('K'))
            if 'Q' in castling:
                castling.pop(castling.index('Q'))
        if self.pieceAt('h1') is None:
            if 'K' in castling:
                castling.pop(castling.index('K'))
        elif self.pieceAt('h1').name != 'rook':
            if 'K' in castling:
                castling.pop(castling.index('K'))
        if self.pieceAt('a1') is None:
            if 'Q' in castling:
                castling.pop(castling.index('Q'))
        elif self.pieceAt('a1').name != 'rook':
            if 'Q' in castling:
                castling.pop(castling.index('Q'))
    
    # Black castling
        if self.pieceAt('e8') is None:
            if 'k' in castling:
                castling.pop(castling.index('k'))
            if 'q' in castling:
                castling.pop(castling.index('q'))
        elif self.pieceAt('e8').name != 'king':
            if 'k' in castling:
                castling.pop(castling.index('k'))
            if 'q' in castling:
                castling.pop(castling.index('q'))
        if self.pieceAt('h8') is None:
            if 'k' in castling:
                castling.pop(castling.index('k'))
        elif self.pieceAt('h8').name != 'rook':
            if 'k' in castling:
                castling.pop(castling.index('k'))
        if self.pieceAt('a8') is None:
            if 'q' in castling:
                castling.pop(castling.index('q'))
        elif self.pieceAt('a8').name != 'rook':
            if 'q' in castling:
                castling.pop(castling.index('q'))
        
        # Update
        if castling:
            self.castling_availability = ''.join(castling.copy())
        else:
            self.castling_availability = '-'
    def copyBoard(self, board) -> None:
        'Function to copy position from another board.'
        copiedboard = board.board.copy()
        for file in range(8):
            for rank in range(8):
                piece = copiedboard[file][rank]
                if piece is not None:
                    self.setPiece(Piece(piece.getName(), piece.getColor(), piece.getPos(), piece.hasMoved(), self), self.convertPosType((file+1, rank+1)))
                else:
                    self.setPiece(None, self.convertPosType((file+1, rank+1)))
        self.active_color = board.fen.activeColor()
        self.castling_availability = board.fen.castlingAvailability()
        self.enpassant_target = board.fen.enpassantTargetSquare()
        self.halfmove_clock = board.fen.halfmoveClock()
        self.fullmove_clock = board.fen.fullmoveClock()
        self.updateAllPieces()
    def identifyDraw(self) -> bool:
        'Returns boolean whether there is a draw from move repetition or fifty-move rule.'
        # Fifty-move rule
        if self.halfmove_clock == 50:
            return True
        else:
            # Threefold repetition
            for position in self.position_history:
                if self.position_history.count(position) == 3:
                    return True
        return False
    def identifyEnPassant(self, piece, target) -> None:
        'Identifies an enpassant target square.'
        if piece.getName() == 'pawn':
            if piece.getColor() == 'white':
                if (int(target[1]) - int(piece.pos[1])) == 2:
                    enpassant_target = self.convertPosType(target)
                    enpassant_target = (enpassant_target[0], enpassant_target[1]-1)
                    self.enpassant_target = self.convertPosType(enpassant_target)
                    return
            if piece.getColor() == 'black':
                if (int(piece.pos[1]) - int(target[1])) == 2:
                    enpassant_target = self.convertPosType(target)
                    enpassant_target = (enpassant_target[0], enpassant_target[1]+1)
                    self.enpassant_target = self.convertPosType(enpassant_target)
                    return
        # If no enpassant valid
        self.enpassant_target = '-'
     
    # Control methods ///
    def movePieceRequest(self, piece, target) -> bool:
        'Executes move piece request if valid.'
        if piece is None:
            return False
        if (self.checkmate is None) or (self.stalemate):
            # Setup /
            flip = {'w': 'b', 'b': 'w'}
            castling_ref = {'g1': ('h1', 'f1'), 'c1': ('a1', 'd1'), 'g8': ('h8', 'f8'), 'c8': ('a8', 'd8')}
            if isinstance(target, tuple):
                target = self.convertPosType(target)
            if target in piece.legalMoves():
                
                # Halfmove clock /
                if (self.pieceAt(target) is not None) or (piece.getName() == 'pawn'):
                    self.halfmove_clock = 0
                else:
                    self.halfmove_clock += 1

                # Castle /
                if piece.getName() == 'king':
                    if target in castling_ref:
                        # Castle
                        rook = self.pieceAt(castling_ref[target][0])
                        if rook is not None:
                            self.setPiece(None, rook.pos)
                            self.setPiece(rook, castling_ref[target][1])
                            rook.setHasMoved(True)

                # Enpassant validation
                if target == self.enpassant_target:
                    if piece.getColor() == 'white':
                        capture = self.convertPosType(target)
                        capture = (capture[0], capture[1]-1)
                        self.setPiece(None, self.convertPosType(capture))
                    elif piece.getColor() == 'black':
                        capture = self.convertPosType(target)
                        capture = (capture[0], capture[1]+1)
                        self.setPiece(None, self.convertPosType(capture))
                self.identifyEnPassant(piece, target)

                # Move Piece /
                self.last_move = (piece.getPos(), target, piece.hasMoved(), self.pieceAt(target))
                self.setPiece(None, piece.getPos())
                self.setPiece(piece, target)
                piece.setHasMoved(True)

                # Fullmove clock /
                if piece.getColor() == 'black':
                    self.fullmove_clock += 1
                # Active color /
                self.active_color = flip[self.active_color]

                # Pawn promote?
                if piece.getName() == 'pawn':
                    if piece.getColor() == 'white':
                        if int(target[1]) == 8:
                            self.promote(piece)
                    if piece.getColor() == 'black':
                        if int(target[1]) == 1:
                            self.promote(piece)
                
                # Update
                self.previous_enpassant_target = self.enpassant_target
                self.updateAllPieces()
                self.savePosition()
                self.castlingChecks()

                # Update fen /
                self.fen.boardToFen(self)

                # Checkmate? /
                if piece.getColor() == 'white':
                    if self.identifyCheckmate('black'):
                        self.checkmate = 'black'
                else:
                    if self.identifyCheckmate('white'):
                        self.checkmate = 'white'

                # Stalemate? /
                if self.checkmate is None:
                    if piece.getColor() == 'white':
                        if self.identifyStalemate('black'):
                            self.stalemate = True
                    else:
                        if self.identifyStalemate('white'):
                            self.stalemate = True
            
                # Draw? /
                if self.identifyDraw():
                    self.draw = True
                
                return True
        return False
    def undoLastMove(self) -> bool:
        'Undos the last move made.'
        if self.last_move is not None:
            flip = {'w': 'b', 'b': 'w'}
            # Fullmove clock /
            if self.pieceAt(self.last_move[1]).getColor() == 'black':
                self.fullmove_clock -= 1
            # Active color /
            self.active_color = flip[self.active_color]
            
            self.pieceAt(self.last_move[1]).setHasMoved(self.last_move[2])
            self.setPiece(self.pieceAt(self.last_move[1]), self.last_move[0])
            self.setPiece(self.last_move[3], self.last_move[1])
            self.enpassant_target = self.previous_enpassant_target

            # Halfmove clock /
            if (self.pieceAt(self.last_move[1]) is not None) or (self.pieceAt(self.last_move[0]).getName() == 'pawn'):
                self.halfmove_clock = 0
            else:
                self.halfmove_clock -= 1

            self.updateAllPieces()
            self.savePosition()
            self.castlingChecks()
            self.fen.boardToFen(self)
            return True
        else:
            return False

class Piece:
    def __init__(self, name: str, color: str, pos: str, has_moved: bool, board: Board):
        self.setAs(name, color, pos, has_moved, board)
    
    # Public Get methods ///
    def getName(self) -> str:
        'Returns name/type of piece. (Getter)'
        return self.name
    def getColor(self) -> str:
        'Returns color of piece. (Getter)'
        return self.color
    def getPos(self, str=True):
        'Returns position of piece as string, optionally formatted as a tuple. (Getter)'
        if str:
            return self.pos
        else:
            return self.convertPosType(self.pos)
    def hasMoved(self) -> bool:
        'Returns a boolean whether the piece has moved from its original position. (Getter)'
        return self.has_moved
    def data(self) -> tuple:
        'Returns tuple of current piece name and color. (Getter)'
        return (self.name, self.color, self.pos, self.has_moved)

    # Public Set methods ///
    def setAs(self, name: str, color: str, pos: str, has_moved: bool, board: Board) -> None:
        'Set or initialise piece attributes. (Setter)'
        self.name: str = name.lower()
        self.color: str = color.lower()
        self.pos: str = pos
        self.board = board
        self.has_moved: bool = has_moved
    def setName(self, name: str) -> None:
        'Sets new name/type of piece as string. (Setter)'
        valid = ['knight', 'bishop', 'rook', 'queen']
        if name in valid:
            self.name = name
    def setColor(self, color: str) -> None:
        'Sets new color of piece as string. (Setter)'
        valid = ['white', 'black']
        if color in valid:
            self.color = color
    def setPos(self, pos) -> None:
        'Sets new position of piece, accepts string or tuple format. (Setter)'
        if isinstance(pos, str):
            self.pos = pos
        elif isinstance(pos, tuple):
            self.pos = self.convertPosType(pos)
    def setHasMoved(self, has_moved: bool) -> None:
        'Sets boolean value as to whether the piece has moved from its original position. (Setter)'
        self.has_moved = has_moved

    # Other methods ///
    def convertPosType(self, pos):
        'Converts position between string and tuple format, returns None if pos is invalid.'
        str_reference = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5,
                         'f': 6, 'g': 7, 'h': 8}
        try:
            # Convert str -> tuple
            if isinstance(pos, str):
                if (int(pos[1]) > 8) or (int(pos[1]) < 1):
                    return None
                return (str_reference[pos[0]], int(pos[1]))
            # Convert tuple -> str
            elif isinstance(pos, tuple):
                int_reference = {v: k for k, v in str_reference.items()}
                if (pos[1] > 8) or (pos[1] < 1):
                    return None
                return int_reference[pos[0]] + str(pos[1])
            else:
                # Invalid type
                return None
        # Pos values outside board boundaries, so invalid
        except KeyError:
            return None
    def calculatePsuedoLegal(self) -> set:
        'Returns set of moves the piece can make before check validation.'
        temporary_moves = []
        pos = self.convertPosType(self.pos)
        if self.color == 'white':
            # Positive offset coefficient
            oc = 1
        else:
            # Negative offset coefficient
            oc = -1

        # Pawn calculation ---
        if self.name == 'pawn':
            offsets = (
                (pos[0], pos[1] + (1*oc)), # forwards
                (pos[0], pos[1] + (2*oc)), # forwards two squares
                (pos[0] - 1, pos[1] + (1*oc)), # capture left
                (pos[0] + 1, pos[1] + (1*oc)) # capture right
            )
            if self.board.pieceAt(offsets[0]) is None:
                temporary_moves.append(offsets[0])
                if self.board.pieceAt(offsets[1]) is None:
                    if (self.color == 'white') and (self.pos[1] == '2'):
                        temporary_moves.append(offsets[1])
                    elif (self.color == 'black') and (self.pos[1] == '7'):
                        temporary_moves.append(offsets[1])
            if self.board.pieceAt(offsets[2]) is not None:
                if self.board.pieceAt(offsets[2]).color != self.color:
                    temporary_moves.append(offsets[2])
            if self.board.pieceAt(offsets[3]) is not None:
                if self.board.pieceAt(offsets[3]).color != self.color:
                    temporary_moves.append(offsets[3])
            # Enpassant
            if self.convertPosType(offsets[2]) == self.board.enpassant_target:
                temporary_moves.append(offsets[2])
            elif self.convertPosType(offsets[3]) == self.board.enpassant_target:
                temporary_moves.append(offsets[3])
        
        # Knight calculation ---
        if self.name == 'knight':
            offsets = (
                (pos[0]+1, pos[1]+2),
                (pos[0]-1, pos[1]+2),
                (pos[0]+1, pos[1]-2),
                (pos[0]-1, pos[1]-2),
                (pos[0]+2, pos[1]+1),
                (pos[0]-2, pos[1]+1),
                (pos[0]+2, pos[1]-1),
                (pos[0]-2, pos[1]-1)
            )
            for offset in offsets:
                if self.board.pieceAt(offset) is not None:
                    if self.board.pieceAt(offset).getColor() != self.color:
                        temporary_moves.append(offset)
                else:
                    temporary_moves.append(offset)

        # Bishop (and psuedo-queen) calculation ---
        if (self.name == 'bishop') or (self.name == 'queen'):
            # Top left diagonal offsets
            for i in range(1, 8):
                offset = (pos[0] - (1*i), pos[1] + (1*i))
                if self.board.pieceAt(offset) is not None:
                    if self.board.pieceAt(offset).getColor() != self.color:
                        temporary_moves.append(offset)
                    break
                else:
                    temporary_moves.append(offset)
            
            # Top right diagonal offsets
            for i in range(1, 8):
                offset = (pos[0] + (1*i), pos[1] + (1*i))
                if self.board.pieceAt(offset) is not None:
                    if self.board.pieceAt(offset).getColor() != self.color:
                        temporary_moves.append(offset)
                    break
                else:
                    temporary_moves.append(offset)

            # Bottom left diagonal offsets
            for i in range(1, 8):
                offset = (pos[0] - (1*i), pos[1] - (1*i))
                if self.board.pieceAt(offset) is not None:
                    if self.board.pieceAt(offset).getColor() != self.color:
                        temporary_moves.append(offset)
                    break
                else:
                    temporary_moves.append(offset)
            
            # Bottom right diagonal offsets
            for i in range(1, 8):
                offset = (pos[0] + (1*i), pos[1] - (1*i))
                if self.board.pieceAt(offset) is not None:
                    if self.board.pieceAt(offset).getColor() != self.color:
                        temporary_moves.append(offset)
                    break
                else:
                    temporary_moves.append(offset)

        # Rook (and psuedo-queen) calculation ---
        if (self.name == 'rook') or (self.name == 'queen'):
            # Forward offsets
                for i in range(1, 8):
                    offset = (pos[0], pos[1] + (1*i))
                    if self.board.pieceAt(offset) is not None:
                        if self.board.pieceAt(offset).getColor() != self.color:
                            temporary_moves.append(offset)
                        break
                    else:
                        temporary_moves.append(offset)
                
                # Backwards offsets
                for i in range(1, 8):
                    offset = (pos[0], pos[1] - (1*i))
                    if self.board.pieceAt(offset) is not None:
                        if self.board.pieceAt(offset).getColor() != self.color:
                            temporary_moves.append(offset)
                        break
                    else:
                        temporary_moves.append(offset)

                # Left offsets
                for i in range(1, 8):
                    offset = (pos[0] - (1*i), pos[1])
                    if self.board.pieceAt(offset) is not None:
                        if self.board.pieceAt(offset).getColor() != self.color:
                            temporary_moves.append(offset)
                        break
                    else:
                        temporary_moves.append(offset)
                
                # Right offsets
                for i in range(1, 8):
                    offset = (pos[0] + (1*i), pos[1])
                    if self.board.pieceAt(offset) is not None:
                        if self.board.pieceAt(offset).getColor() != self.color:
                            temporary_moves.append(offset)
                        break
                    else:
                        temporary_moves.append(offset)

        # King calculation ---
        if self.name == 'king':
            offsets = (
                (pos[0]+1, pos[1]),
                (pos[0]-1, pos[1]),
                (pos[0]+1, pos[1]+1),
                (pos[0]+1, pos[1]-1),
                (pos[0]-1, pos[1]+1),
                (pos[0]-1, pos[1]-1),
                (pos[0], pos[1]+1),
                (pos[0], pos[1]-1)
            )
            # Castling
            if self.color == 'white':
                if ('K' in self.board.castling_availability) and (self.board.pieceAt('f1') is None) and (self.board.pieceAt('g1') is None):
                    temporary_moves.append((pos[0]+2, pos[1]))
                if ('Q' in self.board.castling_availability) and (self.board.pieceAt('d1') is None) and (self.board.pieceAt('c1') is None) and (self.board.pieceAt('b1') is None):
                    temporary_moves.append((pos[0]-2, pos[1]))
            elif self.color == 'black':
                if ('k' in self.board.castling_availability) and (self.board.pieceAt('f8') is None) and (self.board.pieceAt('g8') is None):
                    temporary_moves.append((pos[0]+2, pos[1]))
                if ('q' in self.board.castling_availability) and (self.board.pieceAt('d8') is None) and (self.board.pieceAt('c8') is None) and (self.board.pieceAt('b8') is None):
                    temporary_moves.append((pos[0]-2, pos[1]))

            for offset in offsets:
                if self.board.pieceAt(offset) is not None:
                    if self.board.pieceAt(offset).getColor() != self.color:
                        temporary_moves.append(offset)
                else:
                    temporary_moves.append(offset)

        # Final validation and format
        final_moves = []
        for move in temporary_moves:
            if self.convertPosType(move) is not None:
                final_moves.append(self.convertPosType(move))
        return set(final_moves.copy())
    def checkValidation(self, psuedo_legal_moves: set) -> list:
        'Returns new array of legal moves after check validation.'
        castling_ref = {'g1': ('h1', 'f1'), 'c1': ('a1', 'd1'), 'g8': ('h8', 'f8'), 'c8': ('a8', 'd8')}
        legal_moves = []
        for move in psuedo_legal_moves:
            temporary_board = Board(self.board)
            clone = Piece(self.name, self.color, self.pos, self.has_moved, temporary_board)
            if clone.getName() == 'king':
                    if move in castling_ref:
                        # Castle
                        rook = temporary_board.pieceAt(castling_ref[move][0])
                        if rook is not None:
                            temporary_board.setPiece(None, rook.getPos())
                            temporary_board.setPiece(rook, castling_ref[move][1])
                            rook.setHasMoved(True)
            temporary_board.setPiece(None, clone.pos)
            temporary_board.setPiece(clone, move)
            # If this move does not result in a check, it is legal
            if not temporary_board.checkState(self.color):
                legal_moves.append(move)
        return legal_moves.copy()
    def legalMoves(self) -> list:
        'Returns array of legal moves, as strings, able to be made by this piece. (Getter)'
        psuedo_legal_moves = self.calculatePsuedoLegal()
        return self.checkValidation(psuedo_legal_moves).copy()
    def returnProtectedPieces(self) -> list:
        'Returns a list of pieces being protected by this current piece.'
        protected_pieces = []
        pos = self.convertPosType(self.pos)
        if self.color == 'white':
            # Positive offset coefficient
            oc = 1
        else:
            # Negative offset coefficient
            oc = -1

        # Pawn calculation ---
        if self.name == 'pawn':
            offsets = (
                (pos[0] - 1, pos[1] + (1*oc)), # capture left
                (pos[0] + 1, pos[1] + (1*oc)) # capture right
            )
            for offset in offsets:
                if self.board.pieceAt(offset) is not None:
                    if self.board.pieceAt(offset).getColor() == self.color:
                        protected_pieces.append(self.board.pieceAt(offset))
        
        # Knight calculation ---
        if self.name == 'knight':
            offsets = (
                (pos[0]+1, pos[1]+2),
                (pos[0]-1, pos[1]+2),
                (pos[0]+1, pos[1]-2),
                (pos[0]-1, pos[1]-2),
                (pos[0]+2, pos[1]+1),
                (pos[0]-2, pos[1]+1),
                (pos[0]+2, pos[1]-1),
                (pos[0]-2, pos[1]-1)
            )
            for offset in offsets:
                if self.board.pieceAt(offset) is not None:
                    if self.board.pieceAt(offset).getColor() == self.color:
                        protected_pieces.append(self.board.pieceAt(offset))

        # Bishop (and psuedo-queen) calculation ---
        if (self.name == 'bishop') or (self.name == 'queen'):
            # Top left diagonal offsets
            for i in range(1, 8):
                offset = (pos[0] - (1*i), pos[1] + (1*i))
                if self.board.pieceAt(offset) is not None:
                    if self.board.pieceAt(offset).getColor() == self.color:
                        protected_pieces.append(self.board.pieceAt(offset))
                    break
            
            # Top right diagonal offsets
            for i in range(1, 8):
                offset = (pos[0] + (1*i), pos[1] + (1*i))
                if self.board.pieceAt(offset) is not None:
                    if self.board.pieceAt(offset).getColor() == self.color:
                        protected_pieces.append(self.board.pieceAt(offset))
                    break

            # Bottom left diagonal offsets
            for i in range(1, 8):
                offset = (pos[0] - (1*i), pos[1] - (1*i))
                if self.board.pieceAt(offset) is not None:
                    if self.board.pieceAt(offset).getColor() == self.color:
                        protected_pieces.append(self.board.pieceAt(offset))
                    break
            
            # Bottom right diagonal offsets
            for i in range(1, 8):
                offset = (pos[0] + (1*i), pos[1] - (1*i))
                if self.board.pieceAt(offset) is not None:
                    if self.board.pieceAt(offset).getColor() == self.color:
                        protected_pieces.append(self.board.pieceAt(offset))
                    break

        # Rook (and psuedo-queen) calculation ---
        if (self.name == 'rook') or (self.name == 'queen'):
            # Forward offsets
                for i in range(1, 8):
                    offset = (pos[0], pos[1] + (1*i))
                    if self.board.pieceAt(offset) is not None:
                        if self.board.pieceAt(offset).getColor() == self.color:
                            protected_pieces.append(self.board.pieceAt(offset))
                        break
                
                # Backwards offsets
                for i in range(1, 8):
                    offset = (pos[0], pos[1] - (1*i))
                    if self.board.pieceAt(offset) is not None:
                        if self.board.pieceAt(offset).getColor() == self.color:
                            protected_pieces.append(self.board.pieceAt(offset))
                        break

                # Left offsets
                for i in range(1, 8):
                    offset = (pos[0] - (1*i), pos[1])
                    if self.board.pieceAt(offset) is not None:
                        if self.board.pieceAt(offset).getColor() == self.color:
                            protected_pieces.append(self.board.pieceAt(offset))
                        break
                
                # Right offsets
                for i in range(1, 8):
                    offset = (pos[0] + (1*i), pos[1])
                    if self.board.pieceAt(offset) is not None:
                        if self.board.pieceAt(offset).getColor() == self.color:
                            protected_pieces.append(self.board.pieceAt(offset))
                        break

        # King calculation ---
        if self.name == 'king':
            offsets = (
                (pos[0]+1, pos[1]),
                (pos[0]-1, pos[1]),
                (pos[0]+1, pos[1]+1),
                (pos[0]+1, pos[1]-1),
                (pos[0]-1, pos[1]+1),
                (pos[0]-1, pos[1]-1),
                (pos[0], pos[1]+1),
                (pos[0], pos[1]-1)
            )

            for offset in offsets:
                if self.board.pieceAt(offset) is not None:
                    if self.board.pieceAt(offset).getColor() == self.color:
                        protected_pieces.append(self.board.pieceAt(offset))

        return protected_pieces

class FEN:
    def __init__(self, setter):
        self.string = None
        if isinstance(setter, str):
            self.setString(setter)
        elif isinstance(setter, Board):
            self.boardToFen(setter)
        self.sections = self.string.split(' ')
    
    # Public Get methods ///
    def getString(self) -> str:
        'Returns the whole FEN string. (Getter)'
        return self.string
    def piecePlacement(self) -> str:
        'Returns the piece placement section of the FEN string. (Getter)'
        return self.sections[0]
    def activeColor(self) -> str:
        'Returns the active color section of the FEN string. (Getter)'
        return self.sections[1]
    def castlingAvailability(self) -> str:
        'Returns the castling availability section of the FEN string. (Getter)'
        return self.sections[2]
    def enpassantTargetSquare(self) -> str:
        'Returns the enpassant target square section of the FEN string. (Getter)'
        return self.sections[3]
    def halfmoveClock(self) -> int:
        'Returns the half-move clock section of the FEN string. (Getter)'
        return int(self.sections[4])
    def fullmoveClock(self) -> int:
        'Returns the full-move clock section of the FEN string. (Getter)'
        return int(self.sections[5])
    
    # Public Set methods ///
    def setPiecePlacement(self, piece_placement: str) -> None:
        'Replaces the piece placement section of the FEN string. (Setter)'
        self.sections[0] = piece_placement
        self.updateString()
    def setActiveColor(self, active_color: str) -> None:
        'Replaces the active color section of the FEN string. (Setter)'
        self.sections[1] = active_color
        self.updateString()
    def setCastlingAvailability(self, castling_availability: str) -> None:
        'Replaces the castling availability section of the FEN string. (Setter)'
        self.sections[2] = castling_availability
        self.updateString()
    def setEnpassantTargetSquare(self, enpassant_target: str) -> None:
        'Replaces the enpassant target square section of the FEN string. (Setter)'
        self.sections[3] = enpassant_target
        self.updateString()
    def setHalfmoveClock(self, halfmove_clock) -> None:
        'Replaces the half-move clock section of the FEN string. (Setter)'
        self.sections[4] = str(halfmove_clock)
        self.updateString()
    def setFullmoveClock(self, fullmove_clock) -> None:
        'Replaces the full-move clock section of the FEN string. (Setter)'
        self.sections[5] = str(fullmove_clock)
        self.updateString()
    def boardToFen(self, board: Board) -> None:
        'Converts board position into a FEN string. (Setter)'
        sections = []

        # Section 1 - Piece placement
        piece_ref = {'pawn': 'p', 'rook': 'r', 'bishop': 'b',
                     'knight': 'n','king': 'k', 'queen': 'q'}
        section = []
        empty = 0
        for r in '87654321':
            for f in 'abcdefgh':
                if board.pieceAt(f+r) is not None:
                    if empty:
                        section.append(str(empty))
                        empty = 0
                    if board.pieceAt(f+r).color == 'white':
                        section.append(piece_ref[board.pieceAt(f+r).name].upper())
                    else:
                        section.append(piece_ref[board.pieceAt(f+r).name])
                else:
                    empty += 1
            if empty:
                section.append(str(empty))
                empty = 0
            if r != '1':
                section.append('/')
        sections.append(''.join(section))

        # Section 2 - Active color
        sections.append(board.active_color)

        # Section 3 - Castling availability
        sections.append(board.castling_availability)

        # Section 4 - Enpassant target square
        sections.append(board.enpassant_target)

        # Section 5 - Halfmove clock
        sections.append(str(board.halfmove_clock))

        # Section 6 - Fullmove clock
        sections.append(str(board.fullmove_clock))

        self.sections = sections
        self.updateString()
    def setString(self, fen_string: str) -> None:
        'Replaces current FEN string with a new one. (Setter)'
        self.string = fen_string
        self.sections = self.string.split(' ')

    # Other methods ///
    def updateString(self) -> None:
        'Updates the current FEN string upon a section change.'
        self.string = ' '.join(self.sections)
