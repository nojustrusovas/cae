# #main/engine.py

# class ChessEngine:
#     def __init__(self, depth: int):
#         self.depth = depth
#         self.material_values = {
#             'pawn': 1,
#             'knight': 3,
#             'bishop': 3,
#             'rook': 5,
#             'queen': 9,
#             'king': 0
#         }

#     def staticEvaluation(self, position: list) -> int:
#         'Returns a static evaluation of the current position, which is an array of tuples.'
#         eval = 0
#         for piece in position:
#             if piece[0] is not None:
#                 if piece[1] == 'white':
#                     eval += self.material_values[piece[0]]
#                 else:
#                     eval -= self.material_values[piece[0]]
#         return eval
    
#     def possiblePositions(self, current_position: list) -> list:
#         'Returns an array of possible positions one move ahead of the current position.'

    
#     def minimax(self, position, depth, max: bool) -> int:
#         'Calculates best possible position.'
#         if depth == 0:
#             return self.staticEvaluation(position)
        
#         if max:
#             pass
        
# # class ChessLogicProcessor:
# #     def __init__(self):
# #         self.chessboard = None

# #     def positionToChessboard(self, position):
# #         for piece in position

# #     def calculatePossiblePositions(self, current_position: list) -> list:
# #         'Returns an array of possible positions one move ahead of the current position.'
# #         possible_positions = []