import random
from stockfish import Stockfish

stockfish_path = "Stockfish/stockfish-windows-x86-64-avx2.exe"  
stockfish = Stockfish(path=stockfish_path)

stockfish.update_engine_parameters({
    "Hash": 32,
    "Threads": 2
})

stockfish.set_depth(7)

DEPTH = 1
CHECKMATE = 100000
STALEMATE = 0 


def randomMove(board):
    return random.choice(list(board.legal_moves))

def findBestMoveNegaMinMaxF(board, validMoves):
    global nextMove
    nextMove = None
    maxScore = NegaMinMaxAlphaBeta(board, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if board.turn else -1)
    return nextMove
            
def evaluate_move(board, move):
    if board.is_check():
        return 3 
    if board.is_capture(move):
        return 2
    return 0  
    
def NegaMinMaxAlphaBeta(board, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if board.is_checkmate():
        return -CHECKMATE * turnMultiplier  # Checkmate is the most decisive outcome
    
    if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
        return STALEMATE  # Stalemate or draw condition
    
    if depth == 0:
        stockfish.set_fen_position(board.fen())
        evaluation = stockfish.get_evaluation()

        # Extract the value based on type of evaluation
        if evaluation["type"] == "cp":  
            return turnMultiplier * evaluation["value"]
        
        elif evaluation["type"] == "mate":  
            # Mate is a terminal evaluation; prioritize it
            return turnMultiplier * (100000 if evaluation["value"] > 0 else -100000)

    # Sort moves by heuristic (captures, checks, and evaluated moves)
    sorted_moves = sorted(validMoves, key=lambda move: evaluate_move(board, move), reverse=True)

    maxScore = -CHECKMATE
    for move in sorted_moves:
        board.push(move)
        
        # Check for forced checkmate or stalemate
        if board.is_checkmate():
            score = -CHECKMATE * turnMultiplier
        else:
            score = -NegaMinMaxAlphaBeta(board, board.legal_moves, depth - 1, -beta, -alpha, -turnMultiplier)

        # Update best move
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        
        board.pop()

        # Alpha-beta pruning
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break

    return maxScore
