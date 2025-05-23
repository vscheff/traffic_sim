# Do this before importing pygame to prevent the support prompt from being printed to the terminal
from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "True"

import pygame as pg
from pygame.locals import *

# Local Dependencies
from src.color_map import COLORS
from src.Cell import Cell
from src.Road import Road
from src.utils import Coordinate
from src.Vehicle import Vehicle

# Constants
FPS = 60                            # Target FPS for the game
WINDOW_WIDTH = 1600                 # Initial width of the game window [pixels]
WINDOW_HEIGHT = 900                 # Initial height of the game window [pixels]
SAFE_ZONE = 0.1                     # Ratio of screen size to inset the simulation area [percent]
SIM_FONT = "freesansbold.ttf"       # Font style for text used in simulator
FPS_DISPLAY_RATIO = 2/3             # Ratio of FPS font size to safe area [percent]
CELL_SIZE = 64                      # Size of cells used in simulator [pixels]

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
        self.sprites = {}
        self.cell_matrix = [[]]
        self.active_range = Coordinate(0, 0)
        self.safe_rect = None

        self.prepare_display()
        self.set_initial_condition()

    def set_initial_condition(self):
        self.sprites["Vehicles"] = pg.sprite.Group()
        self.sprites["Vehicles"].add(Vehicle(Coordinate(self.safe_rect.left, self.safe_rect.top)))

    def set_active_range(self):
        self.active_range.y = self.safe_rect.height // CELL_SIZE
        self.active_range.x = self.safe_rect.width // CELL_SIZE
        
        self.grow_cell_matrix()

    def grow_cell_matrix(self):
        grown = False

        if self.active_range.y > len(self.cell_matrix):
            x_range = self.active_range.x - len(self.cell_matrix[0])
            y_range = self.active_range.y - len(self.cell_matrix)
            self.cell_matrix.extend([None for _ in range(x_range)] for _ in range(y_range))
            grown = True

        if self.active_range.x > len(self.cell_matrix[0]):
            for row in self.cell_matrix:
                row.extend(None for _ in range(self.active_range.x - len(row)))
            
            grown = True

        if not grown:
            return

        top = self.safe_rect.top

        for i in range(self.active_range.y):
            left = self.safe_rect.left
            
            for j in range(self.active_range.x):
                if self.cell_matrix[i][j] is None:
                    self.cell_matrix[i][j] = Cell(Coordinate(left, top), CELL_SIZE, CELL_SIZE)

                left += CELL_SIZE

            top += CELL_SIZE

    def prepare_display(self):
        width, height = self.display.get_size()
        
        self.safe_rect = Rect(width * SAFE_ZONE, 
                              height * SAFE_ZONE,
                              width * (1 - 2 * SAFE_ZONE),
                              height * (1 - 2 * SAFE_ZONE)
                             )
        self.safe_rect.width -= self.safe_rect.width % CELL_SIZE
        self.safe_rect.height -= self.safe_rect.height % CELL_SIZE
        self.set_active_range()
        self.adjust_cell_positions()
        self.basic_font = pg.font.Font(SIM_FONT, int(min(width, height) * SAFE_ZONE * FPS_DISPLAY_RATIO))

    def adjust_cell_positions(self):
        if len(self.cell_matrix) < 1:
            return

        top = self.safe_rect.top
        for i in range(self.active_range.y):
            left = self.safe_rect.left
            for j in range(self.active_range.x):
                self.cell_matrix[i][j].adjust_position(top, left)
                left += CELL_SIZE
            top += CELL_SIZE

    def draw_display(self):
        self.display.fill(BG_COLOR)
        self.clear_screen()
        self.draw_fps()
        self.draw_cells()

    def draw_fps(self):
        self.display.blit(*self.make_text(str(round(self.fps_clock.get_fps(), 1)), 0, 0, FPS_COLOR))

    def draw_cells(self):
        for i in range(self.active_range.y):
            for j in range(self.active_range.x):
                self.cell_matrix[i][j].draw(self.display)

    def launch_gui(self):
        while True:
            self.handle_events()
            self.draw_display()
            self.update_sprites()
            pg.display.flip()
            self.fps_clock.tick(FPS)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == QUIT:
                terminate()

            if event.type == VIDEORESIZE:
                self.prepare_display()

            elif event.type == MOUSEBUTTONUP:
                found_collision = False
                for i in range(self.active_range.y):
                    for j in range(self.active_range.x):
                        if self.cell_matrix[i][j].rect.collidepoint(event.pos):
                            self.cell_matrix[i][j].set_sprite(Road(Coordinate(*self.cell_matrix[i][j].rect.topleft)), kill=True)
                            found_collision = True
                            
                            break

                    if found_collision:
                        break

    def update_sprites(self):
        self.sprites["Vehicles"].update()
        for sprite in self.sprites["Vehicles"].sprites():
            if not self.safe_rect.colliderect(sprite.rect):
                sprite.kill()

        self.sprites["Vehicles"].draw(self.display)

    def clear_screen(self):
        pg.draw.rect(self.display, SIM_COLOR, self.safe_rect)

    def make_text(self, text, top, left, color, bg_color=None):
        text_surf = self.basic_font.render(text, True, color, bg_color)
        text_rect = text_surf.get_rect()
        text_rect.topleft = (top, left)

        return text_surf, text_rect


def terminate():
    pg.quit()
    exit("\nProgram Quit... Good Bye!")

