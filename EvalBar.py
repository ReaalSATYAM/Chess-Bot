import chess
import pygame as pg
import sys
import chess.engine

# Initialize Pygame
pg.init()

# Set up the Pygame window
screen_width = 600
screen_height = 600
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("Chess Evaluation Bar")

# Create a chess board
board = chess.Board()

# Initialize running flag for the game loop
running = True

def get_board_evaluation(board):
        return 1000

def draw_evaluation_bar(screen, evaluation):
    bar_width = 30 
    bar_height = 600 
    x_pos = 600  
    y_pos = 0  

    eval_scale = max(-1000, min(evaluation, 1000))  
    eval_percentage = (eval_scale + 1000) / 2000  
    fill_height = int(eval_percentage * bar_height)

    pg.draw.rect(screen, (50, 50, 50), pg.Rect(x_pos, y_pos, bar_width, bar_height))

    # Draw the filled bar based on evaluation value
    if evaluation > 0:
        pg.draw.rect(screen, (255, 255, 255), pg.Rect(x_pos, y_pos + bar_height - fill_height, bar_width, fill_height))  # for positive
    elif evaluation < 0:
        pg.draw.rect(screen, (255, 255, 255), pg.Rect(x_pos, y_pos + bar_height - fill_height, bar_width, fill_height))  # for negative
    else:
        pg.draw.rect(screen, (255, 255, 255), pg.Rect(x_pos, y_pos + bar_height - fill_height, bar_width, fill_height))  

    pg.draw.line(screen, "red", (600, 300), (630, 300), 3)

