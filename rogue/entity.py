from typing import Self, Tuple

import pygame

from rogue.enums import Direction


class Entity(pygame.sprite.Sprite):
    def __init__(self, group: pygame.sprite.Group, blocks_movement: bool, starting_position: Tuple[int, int]):
        super().__init__(group)
        self.blocks_movement = blocks_movement

        self.float_position = pygame.Vector2(starting_position[0] * 16, starting_position[1] * 16)
        self.tile_position = starting_position

        self.facing_direction = Direction.RIGHT

    def simple_distance_to(self, target: Self):
        dx = target.tile_position[0] - self.tile_position[0]
        dy = target.tile_position[1] - self.tile_position[1]
        distance = abs(dx) + abs(dy)
        return distance
