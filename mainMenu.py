import pygame as pg
import sys
from BasicEngine import findBestMoveNegaMinMax
from AdvanceEngine import findBestMoveNegaMinMaxF
import time

BOARD_WIDTH , BOARD_HEIGHT = 630, 600
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION

def homeScreen(screen):

    # Click sound
    pg.mixer.init()
    click_effect = pg.mixer.Sound("SoundEffects/click1.mp3")

    # Background
    bg = pg.image.load("Background/home.png")
    bg = pg.transform.scale(bg, (BOARD_WIDTH , BOARD_HEIGHT))
    screen.blit(bg, (0, 1))

    #Credit 
    font = pg.font.Font('Font/game_over.ttf', 34)
    message_surface = font.render("DEVELOPER~ SATYAM  NAITHANI", True, (255, 255, 255))
    message_rect = message_surface.get_rect(center=(510, 580))
    screen.blit(message_surface, message_rect)

    # background_color = (50, 50, 50)
    text_color = (255, 255, 255)
    button_color = (100, 100, 100)
    button_hover_color = (150, 150, 150)    
    
    # Load images
    playPlayer_image = pg.image.load('Button/1.png')
    playBasicAI_image = pg.image.load('Button/3.png')
    playAdvAI_image = pg.image.load('Button/2.png')
    quit_image = pg.image.load('Button/4.png')

    # Buttons
    playPlayer_button = pg.Rect((BOARD_WIDTH // 4) * 2 - 140, 250, 300, 50)
    playBasicAI_button = pg.Rect((BOARD_WIDTH // 4) * 2 - 140, 320, 300, 50)
    playAdvAI_button = pg.Rect((BOARD_WIDTH // 4) * 2 - 140, 390, 300, 50)
    quit_button = pg.Rect((BOARD_WIDTH // 4) * 2 - 140, 460, 300, 50)

    # Draw rectangles
    pg.draw.rect(screen, button_color, playPlayer_button)
    pg.draw.rect(screen, button_color, playBasicAI_button)
    pg.draw.rect(screen, button_color, playAdvAI_button)
    pg.draw.rect(screen, button_color, quit_button)

    # Blit images
    screen.blit(playPlayer_image, playPlayer_image.get_rect(center=playPlayer_button.center))
    screen.blit(playBasicAI_image, playBasicAI_image.get_rect(center=playBasicAI_button.center))
    screen.blit(playAdvAI_image, playAdvAI_image.get_rect(center=playAdvAI_button.center))
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
                if playPlayer_button.collidepoint(mouse_pos):
                    return True, None
                
                elif playBasicAI_button.collidepoint(mouse_pos):
                    return False, findBestMoveNegaMinMax
                
                elif playAdvAI_button.collidepoint(mouse_pos):
                    return False, findBestMoveNegaMinMaxF
                
                elif quit_button.collidepoint(mouse_pos):
                    click_effect.play()
                    time.sleep(1)
                    pg.quit()
                    sys.exit()
                
                pg.display.flip()
