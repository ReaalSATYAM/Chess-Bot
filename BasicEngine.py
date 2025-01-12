import chess
import random
import numpy as np

CHECKMATE = 100000
STALEMATE = 0 

piece_value = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 4000
}

# Piece-square tables 
piece_square_tables = {
    chess.PAWN: np.array([
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ]),
    chess.KNIGHT: np.array([
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50,
    ]),
    chess.BISHOP: np.array([
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20,
    ]),
    chess.ROOK: np.array([
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0
    ]),
    chess.QUEEN: np.array([
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  10,  10,  5,  0, -5,
     0,  0,  5,  10,  10,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
    ]),
    chess.KING:np.array([
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  0, 10, 30, 20])
}


def flip_table_for_black(piece, square):
    if piece.piece_type == chess.PAWN:
        return piece_square_tables[chess.PAWN][square]
    else:
        return piece_square_tables[piece.piece_type][chess.square_mirror(square)]
    
def findBestMoveNegaMinMax(board, validMoves):
    global nextMove
    nextMove = None
    depth = determine_search_depth(board)
    maxScore = NegaMinMaxAlphaBeta(board, validMoves, depth, depth ,-CHECKMATE, CHECKMATE, 1 if board.turn else -1)
    return nextMove
            
def NegaMinMaxAlphaBeta(board, validMoves, depth, dynamicDepth, alpha, beta, turnMultiplier):
    global nextMove
    if board.is_checkmate():
        return -CHECKMATE * turnMultiplier  
    if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
        return STALEMATE  
    
    if depth == 0 :
        return turnMultiplier * calculate_total_piece_value(board)

    sorted_moves = sorted(validMoves, key=lambda move: evaluate_move(board, move), reverse=True)

    maxScore = -CHECKMATE
    for move in sorted_moves:
        board.push(move)
        score = -NegaMinMaxAlphaBeta(board, board.legal_moves ,depth-1, dynamicDepth, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == dynamicDepth:
                nextMove = move
        board.pop()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

def evaluate_move(board, move):
    if board.is_check():
        return 60  
    if board.is_capture(move):
        return 50  
    return 0  


def calculate_total_piece_value(board):
    total_value = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            value = piece_value.get(piece.piece_type, 0)
            if piece.piece_type in piece_square_tables:
                if piece.color == chess.WHITE:
                    value += piece_square_tables[piece.piece_type][square]
                else:
                    value += flip_table_for_black(piece, square)

            total_value += value if piece.color == chess.WHITE else -value

    
    total_value += evaluate_king_safety(board, chess.WHITE)
    total_value -= evaluate_king_safety(board, chess.BLACK)

    if not board.has_kingside_castling_rights(chess.WHITE) and not board.has_queenside_castling_rights(chess.WHITE):
        total_value -= 60  

    if not board.has_kingside_castling_rights(chess.BLACK) and not board.has_queenside_castling_rights(chess.BLACK):
        total_value += 60  


    total_value += evaluate_pawn_structure(board, chess.WHITE)
    total_value -= evaluate_pawn_structure(board, chess.BLACK)

   
    total_value += 0.1 * len(list(board.legal_moves))  
    return total_value

def evaluate_pawn_structure(board, color):
    value = 0
    pawns = board.pieces(chess.PAWN, color)
    opponent_pawns = board.pieces(chess.PAWN, not color)

    for pawn in pawns:
        file = chess.square_file(pawn)
        # Isolated pawn
        if not any(chess.square_file(p) == file - 1 or chess.square_file(p) == file + 1 for p in pawns):
            value -= 10

        # Doubbled pawn
        if sum(1 for p in pawns if chess.square_file(p) == file) > 1:
            value -= 5

        # Past pawn
        if not any(chess.square_file(opponent_pawn) == file and chess.square_rank(opponent_pawn) > chess.square_rank(pawn)
                   for opponent_pawn in opponent_pawns):
            value += 20  
    return value

def evaluate_king_safety(board, color):
    
    king_square = board.king(color)  
    king_value = 0

    #  Checks if the king is in center 
    center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
    if king_square in center_squares:
        king_value -= 30  

    pawn_shield_value = 0
    file = chess.square_file(king_square)
    rank = chess.square_rank(king_square)

    #8 squars around the king
    surrounding_squares = [
        chess.square(file - 1, rank),  
        chess.square(file + 1, rank),  
        chess.square(file, rank - 1),  
        chess.square(file, rank + 1),  
        chess.square(file - 1, rank - 1),  
        chess.square(file + 1, rank - 1),  
        chess.square(file - 1, rank + 1),  
        chess.square(file + 1, rank + 1)   
    ]

    # Checks if their is a pawn near king
    for position in surrounding_squares:
        if 0 <= chess.square_file(position) < 8 and 0 <= chess.square_rank(position) < 8:
            piece = board.piece_at(position)
            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                pawn_shield_value += 5  

    king_value += pawn_shield_value
    open_file_penalty = 0
    for direction in [-1, 1]:  
        for i in range(1, 8):  
            file_to_check = chess.square(file + direction * i, rank)
            if 0 <= chess.square_file(file_to_check) < 8 and 0 <= chess.square_rank(file_to_check) < 8:
                piece = board.piece_at(file_to_check)
                if piece and piece.piece_type == chess.PAWN:
                    break
                elif piece: 
                    open_file_penalty += 10
                    break
    king_value -= open_file_penalty  

    return king_value

def determine_search_depth(board):
    piece_count = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_count += 1
    
    if piece_count < 32: 
        return 4  
    elif piece_count < 16:  
        return 5
    if piece_count < 10:  
        return 6
    else:  
        return 3

