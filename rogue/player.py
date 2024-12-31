
from os.path import join
from typing import Optional

import pygame

from rogue.entity import Entity
from rogue.enums import AnimState, Direction


class Player(Entity):
    def __init__(self, groups: Optional[pygame.sprite.Group], starting_pos: tuple[int, int], tilemap):
        super().__init__(group=groups,
                         blocks_movement=True,
                         starting_position=starting_pos)

        self.anim_len = 4
        self.images = {
            AnimState.IDLE: [pygame.image.load(
                join("resources", "character", "elf_m", "idle", f"elf_m_idle_anim_f{i}.png")).convert_alpha() for i in range(self.anim_len)],
            AnimState.RUN: [pygame.image.load(
                join("resources", "character", "elf_m", "run", f"elf_m_run_anim_f{i}.png")).convert_alpha() for i in range(self.anim_len)]
        }
        self.map_ref = tilemap
        self.anim_idx = 0
        self.c_anim_state = AnimState.IDLE
        self.image = self.images[self.c_anim_state][self.anim_idx]
        self.anim_timer = 0
        self.rect = pygame.rect.Rect(self.float_position, (16, 16))

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

    def queue_new_animation(self, animation: AnimState):
        if animation != self.c_anim_state:
            self.anim_idx = 0
            self.anim_timer = 0.0
            self.c_anim_state = animation

    def update(self, dt: float):
        # TODO: Animation in baseclass
        self.anim_timer += dt
        if self.anim_timer > 0.08:
            self.anim_timer = 0
            self.anim_idx = (self.anim_idx + 1) % self.anim_len
            self.image = self.images[self.c_anim_state][self.anim_idx]

        if not self.moving and self.moving_direction == Direction.NULL:
            self.queue_new_animation(AnimState.IDLE)

        if self.moving:
            self.queue_new_animation(AnimState.RUN)
            self.direction = self.rect.topleft - pygame.Vector2(self.target_position[0]*16, self.target_position[1]*16)
            if self.direction.length() > 0.01:
                self.direction = self.direction.normalize() if self.direction else self.direction
                self.float_position -= self.direction * self.speed * dt
            else:
                self.float_position = pygame.Vector2(self.target_position[0]*16, self.target_position[1]*16)
                self.moving = False
                self.target_position = None
                self.moving_direction = Direction.NULL

            self.rect.x = self.float_position.x
            self.rect.y = self.float_position.y

        if self.moving_direction in [Direction.LEFT, Direction.RIGHT]:
            self.facing_direction = self.moving_direction

        if self.facing_direction == Direction.LEFT:
            self.image = pygame.transform.flip(
                self.images[self.c_anim_state][self.anim_idx], True, False)

    def move(self, move_dir: Direction) -> None:
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
