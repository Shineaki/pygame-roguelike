from typing import Tuple

import pygame


class Entity(pygame.sprite.Sprite):
    def __init__(self, group: pygame.sprite.Group, starting_position: Tuple[int, int]):
        super().__init__(group)
        self.blocks_movement = True

        self.float_position = pygame.Vector2(starting_position[0] * 16, starting_position[1] * 16)
        self.tile_position = starting_position
