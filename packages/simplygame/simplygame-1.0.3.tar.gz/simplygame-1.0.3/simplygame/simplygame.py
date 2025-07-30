"""
Created 01/07/2025 (FR) | 07/01/2025 (EN)
"""
__version__ = "1.0"
import pygame
from pygame import *
pygame.init()

window = None
running = False
clock = pygame.time.Clock()
def create_window(windowName, width, height):
    """Create a window"""
    global window, running, clavier
    clavier = {}
    window = pygame.display.set_mode([width, height])
    pygame.display.set_caption(windowName)
    window.fill((255, 255, 255))
    running = True
    print("Fenêtre créée, running =", running)
    update()


def update():
    """Update window's objects"""
    pygame.display.flip()

def reset_window():
    """Return as a default stat, with default background color"""
    window.fill((255, 255, 255))

def window_fill(color):
    window.fill(color)

def game_stop():
    """Stop game, close window"""
    global running
    running = False

def tick(fps):
    """Limit frame rate"""
    clock.tick(fps)

def get_version():
    """Return current version of simplygame"""
    return __version__

##Draw
def draw_rect(x,y,width,height,color):
    """Draw a rectangle"""
    pygame.draw.rect(window, color, (x,y,width,height))

def draw_circle(x,y,radius,color):
    """Draw a circle"""
    pygame.draw.circle(window, color, (x,y), radius)



##Events
def recover_event():
    global event
    """
    Allows you to retrieve events
    Events:
    - exit
    - pressed
    - released
    """
    event = pygame.event.poll()

    if event.type == pygame.QUIT:
        running = False
        return "exit"
    
    elif event.type == pygame.KEYDOWN:
        return 'pressed'
    
    elif event.type == pygame.KEYUP:
        return 'released'

    return None

def recover_key():
    """Return character was pressed"""
    global event
    character = pygame.key.name(event.key)
    return character

def is_pressed():
   return pygame.key.get_pressed()