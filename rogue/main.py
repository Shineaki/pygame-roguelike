import random
from enum import Enum
from os.path import join

import numpy as np
import pygame

from rogue.player import Player
from rogue.rect_room import RectangularRoom


class Tiles(Enum):
    WALL = 0
    FLOOR = 1


class TileMap:
    def __init__(self, size: tuple[int]):
        self.tileset = pygame.image.load(
            join("resources", "tiles", "tileset.png")).convert_alpha()
        self.tileset_rect = self.tileset.get_rect()

        self.floor = pygame.Surface((16, 16))
        self.floor.blit(self.tileset, (0, 0), (0, 0, 16, 16))
        self.wall = pygame.Surface((16, 16))
        self.wall.blit(self.tileset, (0, 0), (48, 16, 16, 16))

        self.tiles = np.full(
            size, fill_value=Tiles.WALL, order="F")
        rooms = []
        room_min_size = 3
        room_max_size = 5
        max_rooms = 30
        for _ in range(max_rooms):
            room_width = random.randint(room_min_size, room_max_size)
            room_height = random.randint(room_min_size, room_max_size)

            x = random.randint(1, size[0] - room_width - 1)
            y = random.randint(1, size[1] - room_height - 1)

            new_room = RectangularRoom(x, y, room_width, room_height)
            if any(new_room.intersects(other_room) for other_room in rooms):
                continue

            print(f"{new_room.x1} - {new_room.y1}")

            self.tiles[new_room.inner] = Tiles.FLOOR
            rooms.append(new_room)

        self.tiles_group = pygame.sprite.Group()

        for x in range(size[0]):
            for y in range(size[1]):
                if self.tiles[x][y] == Tiles.FLOOR:
                    c_sprite = pygame.sprite.Sprite(self.tiles_group)
                    c_sprite.image = self.floor
                    c_sprite.rect = pygame.rect.Rect(x*16, y*16, 16, 16)


class Game:
    def __init__(self):
        pygame.init()
        self.screen_size = pygame.Vector2(640, 320)
        self.tilemap_size = (16, 16)
        self.screen_tile_size = (40, 20)

        self.screen = pygame.display.set_mode(
            (640, 320), flags=pygame.SCALED, vsync=0)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0

        self.tilemap = TileMap(self.screen_tile_size)

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
            self.tilemap.tiles_group.draw(self.screen)
            self.player_group.draw(self.screen)

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
