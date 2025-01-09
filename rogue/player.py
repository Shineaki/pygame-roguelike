
from os.path import join
from typing import Optional

import pygame

from rogue.components.animator import Animator
from rogue.entity import Entity
from rogue.enums import AnimState, Direction


class Player(Entity):
    def __init__(self, groups: Optional[pygame.sprite.Group], starting_pos: tuple[int, int], tilemap):
        super().__init__(group=groups,
                         blocks_movement=True,
                         starting_position=starting_pos)
        self.animator = Animator(character_name="elf_m")

        self.image = self.animator.get_current_image()
        self.rect = pygame.rect.Rect(self.float_position, (16, 16))
        self.map_ref = tilemap

        self.direction = pygame.Vector2()
        self.speed = 40

        self.moving = False
        self.moving_direction = Direction.NULL
        self.target_position = None

        self.dir_to_pos = {
            Direction.UP: (0, -1),
            Direction.RIGHT: (1, 0),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
        }

    def update(self, dt: float):
        self.animator.update(dt)

        # TODO: Refactor to avoid overshoot
        # TODO: Refactor target_position to be the same as in the Enemy

        if self.moving:
            self.animator.update_state(AnimState.RUN)
            self.direction = self.float_position - pygame.Vector2(self.target_position[0]*16, self.target_position[1]*16)
            if abs(self.direction.length()) > 1:
                self.direction = self.direction.normalize() if self.direction else self.direction
                self.float_position -= self.direction
            else:
                self.float_position = pygame.Vector2(self.target_position[0]*16, self.target_position[1]*16)
                self.moving = False
                self.target_position = None
                self.moving_direction = Direction.NULL
                # self.animator.update_state(AnimState.IDLE)

            self.rect.x = self.float_position.x
            self.rect.y = self.float_position.y
        elif not self.moving and self.moving_direction == Direction.NULL:
            self.animator.queue_next_animation(AnimState.IDLE)

        self.image = self.animator.get_current_image()
        if self.moving_direction in [Direction.LEFT, Direction.RIGHT]:
            self.facing_direction = self.moving_direction
        if self.facing_direction == Direction.LEFT:
            self.image = pygame.transform.flip(self.animator.get_current_image(), True, False)

    def move(self, move_dir: Direction) -> bool:
        # Invalid movement direction
        if move_dir == Direction.NULL:
            return False

        # We are already moving
        if self.moving:
            return False

        # Check if the target position is blocked
        movement_dir = self.dir_to_pos[move_dir]
        target_pos = (self.tile_position[0] + movement_dir[0], self.tile_position[1] + movement_dir[1])
        if self.map_ref.all_tiles[target_pos[0]][target_pos[1]] == 0:
            return False

        # Valid movement queued
        self.moving = True
        self.moving_direction = move_dir
        self.target_position = target_pos
        self.tile_position = self.target_position

        return True
