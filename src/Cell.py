import pygame as pg


# Local dependencies
from src.utils import Coordinate


class Cell(pg.sprite.Sprite):
    def __init__(self, start_pos, width, height, sprite=None, *args, **kwargs):
        if type(start_pos) != Coordinate:
            raise ValueError

        super().__init__(*args, **kwargs)

        self.sprite = sprite
        self.rect = pg.Rect(start_pos.x, start_pos.y, width, height)

    def set_sprite(self, sprite, kill=False):
        if kill and self.sprite is not None:
            self.sprite.kill()

        self.sprite = sprite

    def adjust_position(self, new_top, new_left):
        self.rect.top = new_top
        self.rect.left = new_left

    def draw(self, display):
        if self.sprite is not None:
            display.blit(self.sprite.image, self.rect)
