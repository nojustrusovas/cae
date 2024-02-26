# main/engine.py
from logic import Board
from stockfish import Stockfish
from random import randint

class ChessEngine:
    def __init__(self, type: str, level: int, color: str, current_position: Board, fast: bool):
        self.color = color
        if type == 'classic':
            self.type = 'classic'
            self.depth = 1
        else:
            self.type = 'stockfish'
            self.stockfish = Stockfish(path='/opt/homebrew/Cellar/stockfish/16/bin/stockfish')
            self.stockfish.set_skill_level(level)
            if fast:
                self.bullet = True
            else:
                self.bullet = False
        self.material_values = {
            'pawn': 1,
            'knight': 3,
            'bishop': 3,
            'rook': 5,
            'queen': 9,
            'king': 10
        }
        self.current_position = current_position
        self.positional_eval = {
            'a1': 0, 'b1': 0, 'c1': 0, 'd1': 0, 'e1': 0, 'f1': 0, 'g1': 0, 'h1': 0,
            'a2': 0, 'b2': 0.15, 'c2': 0.15, 'd2': 0.15, 'e2': 0.15, 'f2': 0.15, 'g2': 0.15, 'h2': 0,
            'a3': 0.1, 'b3': 0.15, 'c3': 0.25, 'd3': 0.25, 'e3': 0.25, 'f3': 0.25, 'g3': 0.15, 'h3': 0.1,
            'a4': 0.15, 'b4': 0.15, 'c4': 0.25, 'd4': 0.5, 'e4': 0.5, 'f4': 0.25, 'g4': 0.15, 'h4': 0.15,
            'a5': 0.15, 'b5': 0.15, 'c5': 0.25, 'd5': 0.5, 'e5': 0.5, 'f5': 0.25, 'g5': 0.15, 'h5': 0.15,
            'a6': 0.1, 'b6': 0.15, 'c6': 0.25, 'd6': 0.25, 'e6': 0.25, 'f6': 0.25, 'g6': 0.15, 'h6': 0.1,
            'a7': 0, 'b7': 0.15, 'c7': 0.15, 'd7': 0.15, 'e7': 0.15, 'f7': 0.15, 'g7': 0.15, 'h7': 0,
            'a8': 0, 'b8': 0, 'c8': 0, 'd8': 0, 'e8': 0, 'f8': 0, 'g8': 0, 'h8': 0,
        }

    def max(self, num1, num2) -> int:
        'Self defined max function because python is useless'
        if num1 > num2:
            return num1
        else:
            return num2 
    def min(self, num1, num2) -> int:
        'Self defined min function because python is useless'
        if num1 < num2:
            return num1
        else:
            return num2

    def staticEvaluation(self, position: Board) -> int:
        'Returns a static evaluation of the current position, which is an array of tuples.'
        eval = 0
        # Piece evaluation
        for piece in position.allPieces():
            if piece.getColor() == 'white':
                eval += self.material_values[piece.name]
                if piece.getName() in ['pawn', 'knight', 'bishop']:
                    eval += self.positional_eval[piece.getPos()]
            elif piece.getColor() == 'black':
                eval -= self.material_values[piece.name]
                if piece.getName() in ['pawn', 'knight', 'bishop']:
                    eval -= self.positional_eval[piece.getPos()]
            # Protecting pieces (ONLY for depth of 1)
            # for protected in piece.returnProtectedPieces():
            #     if piece.getColor() == 'white':
            #         eval += round((self.material_values[protected.getName()] / 2), 1)
            #     elif piece.getColor() == 'black':
            #         eval -= round((self.material_values[protected.getName()] / 2), 1)

        # State evaluation
        if position.checkState('black'):
            eval += 25
        elif position.checkState('white'):
            eval -= 25
        
        if position.checkmateState('black'):
            eval += 500
        elif position.checkmateState('white'):
            eval -= 500
        
        if position.stalemateState():
            eval = 0

        return eval
        
    def possiblePositions(self, current_position: Board, color: str) -> list:
        'Returns an array of possible positions one move ahead of the current position.'
        positions = []
        possible_moves = current_position.allPossibleMoves(color)
        for move in possible_moves:
            cloneboard = Board(current_position)
            pieceat = cloneboard.pieceAt(move[0].getPos())
            position = cloneboard.movePieceRequest(pieceat, move[1])
            if position:
                positions.append(cloneboard)
        return positions
    
    def minimax(self, position: Board, depth, alpha, beta, max: bool) -> int:
        'Calculates best possible position.'
        if depth == 0:
            return self.staticEvaluation(position)
        
        if max: # if white to move
            max_eval = -99999
            possible_positions = self.possiblePositions(position, 'white')
            for child in possible_positions:
                eval = self.minimax(child, depth-1, alpha, beta, False)
                max_eval = self.max(max_eval, eval)
                alpha = self.max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        
        else: # if black to move
            min_eval = 99999
            possible_positions = self.possiblePositions(position, 'black')
            for child in possible_positions:
                eval = self.minimax(child, depth-1, alpha, beta, True)
                min_eval = self.min(min_eval, eval)
                beta = self.min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
    
    def bestMove(self) -> str:
        'Returns best move for engine using minimax in the form \'square1square2\''
        if self.type == 'classic':
            current_eval = self.staticEvaluation(self.current_position)
            best_move = None
            if self.color == 'white':
                best_eval = -999999
                maxing = False
            elif self.color == 'black':
                best_eval = 999999
                maxing = True

            for move in self.current_position.allPossibleMoves(self.color):
                cloneboard = Board(self.current_position)
                cloneboard.movePieceRequest(move[0], move[1])
                eval = self.minimax(cloneboard, self.depth, -999999, 999999, maxing)
                cloneboard.undoLastMove()
                if self.color == 'white':
                    if eval > best_eval:
                        best_eval = eval
                        best_move = move
                    if best_eval > current_eval:
                        return best_move
                elif self.color == 'black':
                    if eval < best_eval:
                        best_eval = eval
                        best_move = move
                    if best_eval < current_eval:
                        return best_move[0].getPos() + best_move[1]
            return best_move[0].getPos() + best_move[1]
        elif self.type == 'stockfish':
            self.stockfish.set_fen_position(self.current_position.fen.string)
            if self.bullet:
                best_move = self.stockfish.get_best_move_time(1000)
            else:
                best_move = self.stockfish.get_best_move_time(randint(1000, 5000))
            return best_move
    
    def updatePosition(self, newfen) -> None:
        'Updates internal position'
        self.current_position = Board(newfen)

# chessboard = Board('rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1')
# engine = ChessEngine('stockfish', 1, 'white', chessboard, True)
# bestmove = engine.bestMove()
# chessboard.movePieceRequest(chessboard.pieceAt(bestmove[0]+bestmove[1]), bestmove[2]+bestmove[3])
# print(chessboard.fen.string)