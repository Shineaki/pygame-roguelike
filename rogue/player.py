
from enum import Enum
from os.path import join
from typing import Optional

import pygame


class AnimState(Enum):
    IDLE = 1
    RUN = 2
    HIT = 3


class Direction(Enum):
    NULL = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


class Player(pygame.sprite.Sprite):
    def __init__(self, groups: Optional[pygame.sprite.Group] = None, starting_pos: tuple[int, int] = (0, 0)):
        super().__init__(groups)
        self.animation_length = 4
        self.images = {
            AnimState.IDLE: [pygame.image.load(
                join("resources", "character", "elf_m", "idle", f"elf_m_idle_anim_f{i}.png")).convert_alpha() for i in range(self.animation_length)],
            AnimState.RUN: [pygame.image.load(
                join("resources", "character", "elf_m", "run", f"elf_m_run_anim_f{i}.png")).convert_alpha() for i in range(self.animation_length)]
        }
        self.animation_idx = 0
        self.current_animation_state = AnimState.IDLE
        self.image = self.images[self.current_animation_state][self.animation_idx]
        self.animation_timer = 0
        self.rect = pygame.rect.Rect(starting_pos, (16, 16))

        self.direction = pygame.Vector2()
        self.speed = 50
        self.current_direction = Direction.RIGHT
        self.position = pygame.Vector2(starting_pos[0], starting_pos[1])

        self.moving = False
        self.moving_direction = Direction.NULL
        self.target_position = None

        self.dir_to_pos = {
            Direction.UP: (0, -16),
            Direction.RIGHT: (16, 0),
            Direction.DOWN: (0, 16),
            Direction.LEFT: (-16, 0),
        }

    def queue_new_animation(self, animation: AnimState):
        if animation != self.current_animation_state:
            self.animation_idx = 0
            self.animation_timer = 0.0
            self.current_animation_state = animation

    def update(self, dt: float):
        self.animation_timer += dt
        if self.animation_timer > 0.08:
            self.animation_timer = 0
            self.animation_idx = (self.animation_idx +
                                  1) % self.animation_length
            self.image = self.images[self.current_animation_state][self.animation_idx]

        if not self.moving:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_d]:
                self.moving_direction = Direction.RIGHT
            if keys[pygame.K_a]:
                self.moving_direction = Direction.LEFT
            if keys[pygame.K_s]:
                self.moving_direction = Direction.DOWN
            if keys[pygame.K_w]:
                self.moving_direction = Direction.UP
            if self.moving_direction != Direction.NULL:
                self.moving = True
                self.target_position = pygame.Vector2(
                    self.rect.centerx + self.dir_to_pos[self.moving_direction][0], self.rect.centery + self.dir_to_pos[self.moving_direction][1])
            else:
                self.queue_new_animation(AnimState.IDLE)

        if self.moving:
            self.queue_new_animation(AnimState.RUN)
            self.direction = self.rect.center - self.target_position
            if self.direction != [0, 0]:
                self.direction = self.direction.normalize() if self.direction else self.direction
                self.position -= self.direction * self.speed * dt
                self.rect.x = self.position.x
                self.rect.y = self.position.y
            else:
                self.moving = False
                self.target_position = None
                self.moving_direction = Direction.NULL

        if self.moving_direction in [Direction.LEFT, Direction.RIGHT]:
            self.current_direction = self.moving_direction

        if self.current_direction == Direction.LEFT:
            self.image = pygame.transform.flip(
                self.images[self.current_animation_state][self.animation_idx], True, False)
