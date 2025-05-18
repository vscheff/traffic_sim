# Do this before importing pygame to prevent the support prompt from being printed to the terminal
from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "True"

import pygame as pg
from pygame.locals import *

# Local Dependencies
from src.color_map import COLORS

# Constants
FPS = 60                            # Target FPS for the game
WINDOW_WIDTH = 1600                 # Initial width of the game window [pixels]
WINDOW_HEIGHT = 900                 # Initial height of the game window [pixels]
SAFE_ZONE = 0.1                     # Ratio of screen size to inset the simulation area [percent]

# Color Constants
BG_COLOR = COLORS["dark_gray"]

class GraphicsEngine:
    def __init__(self):
        pg.init()

        self.display = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), RESIZABLE)
        self.fps_clock = pg.time.Clock()
        self.draw_display()

    def draw_display(self):
        self.display.fill(BG_COLOR)
        pg.display.flip()

    def launch_gui(self):
        while True:
            self.event_handler()
            self.fps_clock.tick(FPS)

    def event_handler(self):
        for event in pg.event.get():
            if event.type == QUIT:
                terminate()
    
    def clear_screen(self):
        width, height = self.display.get_size()


def terminate():
    pg.quit()
    exit("\nProgram Quit... Good Bye!")

