import pygame as pg


# Local dependencies
from src.utils import Coordinate


class Cell(pg.sprite.Sprite):
    def __init__(self, start_pos, *args, **kwargs):
        if type(start_pos) != Coordinate:
            raise ValueError

        super().__init__(*args, **kwargs)

        self.image = pg.image.load("textures/Cell.png")
        self.rect = pg.Rect(start_pos.x, start_pos.y, *self.image.get_size())
