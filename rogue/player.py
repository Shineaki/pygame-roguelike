
from enum import Enum
from os.path import join
from typing import Optional

import pygame


class AnimState(Enum):
    IDLE = 1
    RUN = 2
    HIT = 3


class Direction(Enum):
    LEFT = 1
    RIGHT = 2


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
        self.speed = 100
        self.current_direction = Direction.RIGHT
        self.position = pygame.Vector2(starting_pos[0], starting_pos[1])

    def update(self, dt: float):
        self.animation_timer += 1
        if self.animation_timer > 5:
            self.animation_timer = 0
            self.animation_idx = (self.animation_idx +
                                  1) % self.animation_length
            self.image = self.images[self.current_animation_state][self.animation_idx]

        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

        if self.direction.length() > 0.0:
            self.current_animation_state = AnimState.RUN
        else:
            self.current_animation_state = AnimState.IDLE
        if self.direction.x > 0:
            self.current_direction = Direction.RIGHT
        if self.direction.x < 0:
            self.current_direction = Direction.LEFT

        if self.current_direction == Direction.LEFT:
            self.image = pygame.transform.flip(
                self.images[self.current_animation_state][self.animation_idx], True, False)
        self.position += self.direction * self.speed * dt
        self.rect.x = self.position.x
        self.rect.y = self.position.y
