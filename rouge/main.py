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
    def __init__(self, groups: Optional[pygame.sprite.Group] = None):
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
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.direction = pygame.Vector2()
        self.speed = 100
        self.current_direction = Direction.RIGHT
        self.position = pygame.Vector2(16, 16)

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
        self.rect.center = self.position


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (640, 360), flags=pygame.SCALED, vsync=0)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0

        self.player_pos = pygame.Vector2(
            self.screen.get_width() / 2,
            self.screen.get_height() / 2
        )

        self.player_group = pygame.sprite.Group()
        self.object = Player(self.player_group)

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # fill the screen with a color to wipe away anything from last frame
            self.screen.fill("black")

            self.player_group.update(self.dt)
            self.player_group.draw(self.screen)

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
