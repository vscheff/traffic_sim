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
SIM_FONT = "freesansbold.ttf"       # Font style for text used in simulator
FPS_DISPLAY_RATIO = 2/3             # Ratio of FPS font size to safe area [percent]

# Color Constants
BG_COLOR = COLORS["dark_gray"]
SIM_COLOR = COLORS["green"]
FPS_COLOR = COLORS["white"]

class GraphicsEngine:
    def __init__(self):
        pg.init()

        self.display = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), RESIZABLE)
        self.fps_clock = pg.time.Clock()
        self.basic_font = None

        self.prepare_display()

    def prepare_display(self):
        width, height = self.display.get_size()
        self.basic_font = pg.font.Font(SIM_FONT, int(min(width, height) * SAFE_ZONE * FPS_DISPLAY_RATIO))

    def draw_display(self):
        self.display.fill(BG_COLOR)
        self.clear_screen()
        self.draw_fps()
        pg.display.flip()

    def draw_fps(self):
        self.display.blit(*self.make_text(str(round(self.fps_clock.get_fps(), 1)), 0, 0, FPS_COLOR))

    def launch_gui(self):
        while True:
            self.handle_events()
            self.draw_display()
            self.fps_clock.tick(FPS)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == QUIT:
                terminate()

            if event.type == VIDEORESIZE:
                self.prepare_display()
    
    def clear_screen(self):
        width, height = self.display.get_size()
        rect = Rect(width * SAFE_ZONE, height * SAFE_ZONE, width * (1 - 2 * SAFE_ZONE), height * (1 - 2 * SAFE_ZONE))
        pg.draw.rect(self.display, SIM_COLOR, rect)

    def make_text(self, text, top, left, color, bg_color=None):
        text_surf = self.basic_font.render(text, True, color, bg_color)
        text_rect = text_surf.get_rect()
        text_rect.topleft = (top, left)

        return text_surf, text_rect

def terminate():
    pg.quit()
    exit("\nProgram Quit... Good Bye!")

