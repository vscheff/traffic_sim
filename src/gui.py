# Do this before importing pygame to prevent the support prompt from being printed to the terminal
from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "True"

import pygame as pg
from pygame.locals import *

# Local Dependencies
import src.actions as ACT
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
TOOLBAR_DISPLAY_RATIO = 0.25        # Ratio of toolbar font size to safe area [percent]
TOOLBAR_OFFSET = 10                 # Distance between toolbar items [pixels]
TOOLBAR_MARGIN = 10                 # Distance from the edge of the screen to draw toolbar items [pixels]
CELL_SIZE = 64                      # Size of cells used in simulator [pixels]

# Color Constants
BG_COLOR = COLORS["dark_gray"]
SIM_COLOR = COLORS["green"]
FPS_COLOR = COLORS["white"]
TOOLBAR_COLOR = COLORS["light_gray"]

class GraphicsEngine:
    def __init__(self):
        pg.init()

        self.display = None
        self.fps_clock = pg.time.Clock()
        self.fonts = {}
        self.tools = []
        self.active_tool = None
        self.sprites = {}
        self.cell_matrix = [[]]
        self.active_range = Coordinate(0, 0)
        self.safe_rect = None
        self.hovering = False

    #########################
    # Initial setup methods #
    #########################

    def launch_gui(self):
        self.display = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), RESIZABLE)
        pg.display.set_caption("Traffic Simulator 2025")
        self.prepare_display()
        self.set_initial_condition()
        self.execution_loop()

    def set_initial_condition(self):
        self.sprites["Vehicles"] = pg.sprite.Group()
        self.sprites["Vehicles"].add(Vehicle(Coordinate(self.safe_rect.left, self.safe_rect.top)))

        self.tools.append({"image": pg.image.load("textures/Eraser.png"), "rect": None, "action": ACT.ERASE})
        self.tools.append({"image": pg.image.load("textures/Single_Lane_Two_Way_Road.png"), "rect": None, "action": ACT.ROAD})

    #################################
    # Frame-by-frame update methods #
    #################################

    def execution_loop(self):
        while True:
            self.draw_display()
            self.update_sprites()
            self.fps_clock.tick(FPS)
            self.handle_events()
            self.draw_mouse()
            pg.display.flip()

    def draw_display(self):
        self.display.fill(BG_COLOR)
        pg.draw.rect(self.display, SIM_COLOR, self.safe_rect)
        self.display.blit(*self.make_text("FPS", str(round(self.fps_clock.get_fps(), 1)), 0, 0, FPS_COLOR))
        self.draw_toolbar()
        self.draw_cells()

    def draw_toolbar(self):
        font_surf, font_rect = self.make_text("Toolbar", "Toolbar", 0, self.safe_rect.top, FPS_COLOR)
        self.display.blit(font_surf, font_rect)
        
        top = font_rect.bottom + TOOLBAR_OFFSET
        for tool in self.tools:
            rect = pg.Rect(TOOLBAR_MARGIN, top, *tool["image"].get_size())
            self.display.blit(tool["image"], rect)
            tool["rect"] = rect
            top += rect.height + TOOLBAR_OFFSET

    def draw_cells(self):
        for i in range(self.active_range.y):
            for j in range(self.active_range.x):
                self.cell_matrix[i][j].draw(self.display)

    def update_sprites(self):
        self.sprites["Vehicles"].update()
        for sprite in self.sprites["Vehicles"].sprites():
            if not self.safe_rect.colliderect(sprite.rect):
                sprite.kill()

        self.sprites["Vehicles"].draw(self.display)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == QUIT:
                terminate()

            if event.type == VIDEORESIZE:
                self.prepare_display()

            elif event.type == MOUSEMOTION:
                self.hovering = False
                cursor = SYSTEM_CURSOR_HAND if any(i["rect"].collidepoint(event.pos) for i in self.tools) else SYSTEM_CURSOR_ARROW

                if self.active_tool is None or cursor == SYSTEM_CURSOR_HAND:
                    pg.mouse.set_visible(True)
                    self.hovering = True
                    pg.mouse.set_cursor(cursor)

            elif event.type == MOUSEBUTTONUP:
                if self.safe_rect.collidepoint(event.pos):
                    if self.active_tool is None:
                        continue

                    clicked_cell = self.cell_matrix[(event.pos[1] - self.safe_rect.top) // CELL_SIZE][(event.pos[0] - self.safe_rect.left) // CELL_SIZE]

                    if self.active_tool["action"] is ACT.ERASE:
                        clicked_cell.set_sprite(None, kill=True)
                    else:
                        clicked_cell.set_sprite(self.active_tool["action"](Coordinate(*clicked_cell.rect.topleft)), kill=True)
                else:
                    for tool in self.tools:
                        if tool["rect"].collidepoint(event.pos):
                            self.active_tool = tool

    def draw_mouse(self):
        if self.active_tool is None or self.hovering:
            return

        pg.mouse.set_visible(False)
        rect = self.active_tool["rect"].copy()
        rect.center = pg.mouse.get_pos()
        self.display.blit(self.active_tool["image"], rect)

    #########################
    # Screen resize methods #
    #########################

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
        self.fonts["FPS"] = pg.font.Font(SIM_FONT, int(min(width, height) * SAFE_ZONE * FPS_DISPLAY_RATIO))
        self.fonts["Toolbar"] = pg.font.Font(SIM_FONT, int(width * SAFE_ZONE * TOOLBAR_DISPLAY_RATIO))

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

    ###################
    # Utility methods #
    ###################

    def make_text(self, font, text, top, left, color, bg_color=None):
        text_surf = self.fonts[font].render(text, True, color, bg_color)
        text_rect = text_surf.get_rect()
        text_rect.topleft = (top, left)

        return text_surf, text_rect


def terminate():
    pg.quit()
    exit("\nProgram Quit... Good Bye!")
