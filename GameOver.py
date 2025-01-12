import chess
import pygame as pg
import sys
import time

BOARD_WIDTH , BOARD_HEIGHT = 630,600
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION

def gameOverScreen(screen, message):
    pg.mixer.init()
    click_effect = pg.mixer.Sound("SoundEffects/click1.mp3")
    bg = pg.image.load("Background/gameOver.png")
    bg = pg.transform.scale(bg, (BOARD_WIDTH , BOARD_HEIGHT))
    screen.blit(bg, (0, 1))

    button_color = (100, 100, 100) 
    text_color = (255, 255, 255)

    font = pg.font.Font('Font/game_over.ttf', 80)
    message_surface = font.render(message, True, text_color)
    message_rect = message_surface.get_rect(center=(BOARD_WIDTH // 2, 240))
    screen.blit(message_surface, message_rect)

    #Credit 
    crFont = pg.font.Font('Font/game_over.ttf', 34)
    message_surface = crFont.render("DEVELOPER~ SATYAM  NAITHANI", True, (255, 255, 255))
    message_rect = message_surface.get_rect(center=(510, 580))
    screen.blit(message_surface, message_rect)


    # Load images
    restart_image = pg.image.load('Button/5.png')
    quit_image = pg.image.load('Button/4.png')


    restart_button = pg.Rect((BOARD_WIDTH // 4) * 2 - 140, 300, 300, 50)
    quit_button = pg.Rect((BOARD_WIDTH // 4) * 2 - 140, 400, 300, 50)
    
    # Draw rectangles
    pg.draw.rect(screen, button_color, restart_button)
    pg.draw.rect(screen, button_color, quit_button)

    # Blit images
    screen.blit(restart_image, restart_image.get_rect(center=restart_button.center))
    screen.blit(quit_image, quit_image.get_rect(center=quit_button.center))

    pg.display.flip()

    # Wait for user interaction
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()
                if restart_button.collidepoint(mouse_pos):
                    click_effect.play()
                    time.sleep(1)
                    return True
                
                elif quit_button.collidepoint(mouse_pos):
                    click_effect.play()
                    time.sleep(1)
                    pg.quit()
                    sys.exit()

                pg.display.flip()

