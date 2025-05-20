import pygame as pg

# Local Dependencies
from src.color_map import COLORS
from src.utils import Coordinate

class Vehicle(pg.sprite.Sprite):
    def __init__(self, start_pos, *args, **kwargs):
        if type(start_pos) != Coordinate:
            raise ValueError

        super().__init__(*args, **kwargs)
        
        self.image = pg.Surface([99, 33])
        self.image.fill(COLORS["black"])
        self.rect = pg.Rect(start_pos.x, start_pos.y, *self.image.get_size())

    def update(self):
        self.rect.x += 3
