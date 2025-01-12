import chess
import pygame as pg
import sys
from BasicEngine import findBestMoveNegaMinMax
import threading
from AdvanceEngine import findBestMoveNegaMinMaxF
from EvalBar import draw_evaluation_bar
from stockfish import Stockfish
from GameOver import gameOverScreen
from mainMenu import homeScreen
import time

# Constants
BOARD_WIDTH , BOARD_HEIGHT = 630, 600
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
IMAGES = {}

playerOne = True
playerTwo = True
evaluationFunction = None

flip = False

stockfish_path = "Stockfish/stockfish-windows-x86-64-avx2.exe" 
stockfish = Stockfish(path=stockfish_path)
evaluation = 0
stockfish.update_engine_parameters({
    "Hash": 32, 
    "Threads": 2
})

stockfish.set_depth(9)

# Initialize Pygame and the board
pg.init()
screen = pg.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))

# Sound effects
pg.mixer.init()
move_effect = pg.mixer.Sound("SoundEffects/move.mp3")
check_effect = pg.mixer.Sound("SoundEffects/check.mp3")
capture_effect = pg.mixer.Sound("SoundEffects/capture.mp3")
castle_effect = pg.mixer.Sound("SoundEffects/castle.mp3")
checkMate_effect = pg.mixer.Sound("SoundEffects/game-end.mp3")
start_effect = pg.mixer.Sound("SoundEffects/game-start.mp3")
end_effect = pg.mixer.Sound("SoundEffects/game-end.mp3")
promote_effect = pg.mixer.Sound("SoundEffects/promote.mp3")


running = True
board = chess.Board()
clicked_square = None  # Tracks the square selected by the user
moveLog = []  # Stores moves made by user

# For threading
ai_move_result = None
ai_move_lock = threading.Lock()


def getEvaluation(board):
    stockfish.set_fen_position(board.fen())
    evaluation = stockfish.get_evaluation()
    # Extract the value based on type of evaluation
    if evaluation["type"] == "cp":  
        return evaluation['value']  
    elif evaluation["type"] == "mate":  
        return 1000 if evaluation["value"] > 0 else -1000  # Handle checkmate evaluations
    
# Load images
def loadImages():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'br', 'bn', 'bb', 'bk', 'bq']
    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load("pieces/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))

# Draw board with alternating colors
def drawBoard(screen):
    colors = [(240, 217, 181), (181, 136, 99)]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[(row + column) % 2]
            pg.draw.rect(screen, color, pg.Rect(column * SQUARE_SIZE , row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Draw pieces
def drawPieces(screen, board):
    for row in range(8):
        for col in range(8):
            index = (row * 8 + col)
            piece = board.piece_at(index)
            if piece is not None:
                if flip == True:
                    if piece.color == chess.WHITE:
                        screen.blit(IMAGES[f'w{piece.symbol().upper()}'], pg.Rect((7 - col) * SQUARE_SIZE, (row) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                    else:
                        screen.blit(IMAGES[f'b{piece.symbol()}'], pg.Rect((7 - col) * SQUARE_SIZE, (row) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                else:
                    if piece.color == chess.WHITE:
                        screen.blit(IMAGES[f'w{piece.symbol().upper()}'], pg.Rect(col * SQUARE_SIZE, (7-row) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                    else:
                        screen.blit(IMAGES[f'b{piece.symbol()}'], pg.Rect(col * SQUARE_SIZE, (7-row) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Get legal moves for a square
def getLegalMoves(square):
    return [move for move in board.legal_moves if move.from_square == square]

# Show piece promotion window
def showPromotionWindow(screen, end_square, color):
    global humanTurn
    if not humanTurn:
         return chess.QUEEN
    
    promotion_window_width = SQUARE_SIZE
    promotion_window_height = SQUARE_SIZE * 4
    promotion_window = pg.Surface((promotion_window_width, promotion_window_height))
    promotion_window.fill((200, 200, 200))  # Light gray background

    if color == 'w':
        pieces = ['Q', 'R', 'B', 'N']  
        piece_images = [IMAGES[f'{color}{piece}'] for piece in pieces]
    else:
        pieces = ['q', 'r', 'b', 'n']
        piece_images = [IMAGES[f'{color}{piece}'] for piece in pieces]

    # Draw each piece in the promotion window
    for i, piece_image in enumerate(piece_images):
        y_pos = i * SQUARE_SIZE
        promotion_window.blit(piece_image, (0, y_pos))

    # Calculate window position
    col = chess.square_file(end_square)
    row = chess.square_rank(end_square)

    if color == 'w':
        if flip == True:
            screen_y = (row) * SQUARE_SIZE - promotion_window_height
            screen_x = (7 - col) * SQUARE_SIZE 
        else:
            screen_y = (7 - row) * SQUARE_SIZE
            screen_x = col * SQUARE_SIZE
    else:
        if flip == True:
            screen_y = (row) * SQUARE_SIZE 
            screen_x = (7 - col) * SQUARE_SIZE 
        else:
            screen_y = (7 - row) * SQUARE_SIZE - promotion_window_height
            screen_x = col * SQUARE_SIZE


    # Blit the promotion window on the main screen
    screen.blit(promotion_window, (screen_x, screen_y))
    pg.display.flip()

    # Map selected pieces to chess constants
    realPieces = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]

    # Wait for user to select a promotion piece
    while True:
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pg.mouse.get_pos()
                if screen_x <= mouse_x < screen_x + promotion_window_width and screen_y <= mouse_y < screen_y + promotion_window_height:
                    selected_index = (mouse_y - screen_y) // SQUARE_SIZE
                    return realPieces[selected_index]


def highlightSquares(screen, valid_moves, square_selected=None, hovered_square=None):
    global flip
    if square_selected is not None:
        row, col = divmod(square_selected, 8)
        rect = pg.Rect(((7 - col) if flip else col) * SQUARE_SIZE, 
                       (row if flip else (7 - row)) * SQUARE_SIZE, 
                       SQUARE_SIZE, SQUARE_SIZE)
        pg.draw.rect(screen, pg.Color('blue'), rect, width=3)  # Blue outline for selected square

        # Highlight valid moves
        for move in valid_moves:
            end_row, end_col = divmod(move.to_square, 8)
            rect = pg.Rect(((7 - end_col) if flip else end_col) * SQUARE_SIZE, 
                           (end_row if flip else (7 - end_row)) * SQUARE_SIZE, 
                           SQUARE_SIZE, SQUARE_SIZE)
            pg.draw.rect(screen, (220, 20, 60), rect, width=3)  # Yellow outline for valid move

    if hovered_square is not None:
        # Highlight the hovered square
        row, col = divmod(hovered_square, 8)
        rect = pg.Rect(((7 - col) if flip else col) * SQUARE_SIZE,
                   (row if flip else (7 - row)) * SQUARE_SIZE,
                   SQUARE_SIZE, SQUARE_SIZE)
        pg.draw.rect(screen, pg.Color('blue'), rect, width=3)  # Solid blue square

# Make a move if valid
def makeMove(start_square, end_square):
    global humanTurn, evaluation
    piece = board.piece_at(start_square)
    move = None
    promote = False
    capture = False
    castle = False
    check = False

    if piece is not None:
        if piece.piece_type == chess.PAWN and piece.color == chess.WHITE and board.turn:
            if chess.square_rank(start_square) == 6 and chess.square_rank(end_square) == 7:
                promotion_piece = showPromotionWindow(screen, end_square, 'w')
                move = chess.Move(start_square, end_square, promotion=promotion_piece)
                promote = True

        # Check for black pawn promotion
        elif piece.piece_type == chess.PAWN and piece.color == chess.BLACK and (not board.turn):
            if chess.square_rank(start_square) == 1 and chess.square_rank(end_square) == 0:
                promotion_piece = showPromotionWindow(screen, end_square, 'b')
                move = chess.Move(start_square, end_square, promotion=promotion_piece)
                promote = True

    # Handle regular moves (non-promotion)
    if move is None:
        move = chess.Move(start_square, end_square)

    # Validate and execute the move
    if move in board.legal_moves:
        if board.is_capture(move):
            capture = True
        elif board.is_castling(move):
            castle = True
        board.push(move)  # Temporarily apply the move
        if board.is_check():
            check = True 
        board.pop()  

        board.push(move)
        evaluation = getEvaluation(board)
        pg.display.flip()
        
        if check:
            check_effect.play()
        elif promote:
            promote_effect.play()
        elif capture:
            capture_effect.play()
        elif castle:
            castle_effect.play()
        else:
            move_effect.play()
   

def ai_move_thread(board, legal_moves):
    global ai_move_result
    AImove = evaluationFunction(board, legal_moves)
    with ai_move_lock:
        ai_move_result = AImove 

# Main game loop
def main():
    global board, screen, humanTurn, ai_move_result, playerOne, playerTwo, running, clicked_square, evaluation, flip, evaluationFunction
    # Loading home screen 
    playerTwo, evaluationFunction = homeScreen(screen)
    start_effect.play()
    loadImages()
    while running:
        humanTurn = ( board.turn and playerOne) or(not board.turn and playerTwo)
        drawBoard(screen)
        drawPieces(screen, board)
        draw_evaluation_bar(screen, evaluation)

        # Get mouse position and highlight hovered square
        mouse_pos = pg.mouse.get_pos()
        col, row = mouse_pos[0] // SQUARE_SIZE, mouse_pos[1] // SQUARE_SIZE
        if flip:
            hovered_square = chess.square(7 - col, row)
        else:
            hovered_square = chess.square(col, 7 - row)

        # Highlight hovered square
        highlightSquares(screen, getLegalMoves(clicked_square), clicked_square, hovered_square)

        if clicked_square is not None:
            legal_moves = getLegalMoves(clicked_square)
            highlightSquares(screen, legal_moves, clicked_square)
            drawPieces(screen, board)

        if board.is_game_over():
            drawPieces(screen, board)
            pg.display.flip()
            end_effect.play()
            time.sleep(1)
            if board.is_checkmate():
                winner = "Black" if board.turn else "White" 
                restart = gameOverScreen(screen, f"Checkmate! {winner} wins!")

            elif board.is_stalemate():
                restart = gameOverScreen(screen, "Stalemate!")

            elif board.is_insufficient_material():
                restart = gameOverScreen(screen, "Stalemate!")

            elif board.is_seventyfive_moves():
                restart = gameOverScreen(screen, "Draw by seventy-five move rule!")

            elif board.is_fivefold_repetition():
                restart = gameOverScreen(screen, "Draw by fivefold repetition!")
            pg.display.flip()

            if restart:
                # Reset the board to the initial position
                board.set_fen(chess.STARTING_FEN)
            else:
                running = False
            continue 

        pg.display.flip()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                pg.quit()
                sys.exit()

            elif event.type == pg.MOUSEBUTTONDOWN:
                location = pg.mouse.get_pos()
                col = location[0] // SQUARE_SIZE
                row = location[1] // SQUARE_SIZE
                if flip == True:
                    newRow = row
                    newCol = 7 - col
                else:
                    newRow = 7 - row
                    newCol = col
                square = chess.square(newCol, newRow)

                if clicked_square is not None:
                    if makeMove(clicked_square, square):
                        clicked_square = None  
                    else:
                        clicked_square = square 
                else:
                    clicked_square = square 

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:  # Flip the board 
                    flip = not(flip) 
                    drawPieces(screen, board)
        
        if not humanTurn and board.legal_moves.count() != 0:
            ai_move_result = None
            ai_thread = threading.Thread(target = ai_move_thread, args=(board, board.legal_moves))
            ai_thread.start()
            ai_thread.join() 
            if ai_move_result is not None:
                makeMove(ai_move_result.from_square, ai_move_result.to_square)
    pg.quit()

main()
