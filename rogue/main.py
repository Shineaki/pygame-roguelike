import json
import random
from os.path import join
from typing import Iterator

import numpy as np
import pygame
import tcod

from rogue.enums import Tiles
from rogue.player import Player
from rogue.rect_room import RectangularRoom


class TileMap:
    def __init__(self, size: tuple[int]):
        self.size = size
        self.player_position = (0, 0)
        self.tileset = pygame.image.load(
            join("resources", "tiles", "ff.png")).convert_alpha()

        self.tile_images = {
            i: self.create_tile_image(i) for i in range(256+1)
        }

        self.tiles = np.full(size, fill_value=Tiles.WALL, order="F")
        self.rooms: list[RectangularRoom] = []
        self.tiles_group = pygame.sprite.Group()

        self.generate_dungeon()
        # self.generate_debug_dungeon()
        self.final_tiles = self.tiles.copy()
        self.decide_tile_types()
        self.draw_tiles()

    def create_tile_image(self, idx: int) -> pygame.Surface:
        tmp_surface = pygame.Surface((16, 16))
        x = idx % 24
        y = idx // 24
        tmp_surface.blit(self.tileset, (0, 0), (x * 16, y * 16, 16, 16))
        return tmp_surface

    def generate_debug_dungeon(self):
        dungeon = [
            "########################################",
            "#### # ### #############################",
            "############ ###########################",
            "##### #### #############################",
            "########################################",
            "########################################",
            "########################################",
            "########################################",
            "########################################",
            "######## ########## # ##################",
            "########## #############################",
            "######### ######### ####################",
            "########################################",
            "########################################",
            "########################################",
            "########################################",
            "########################################",
            "########################################",
            "########################################",
            "########################################",
        ]
        for y in range(len(dungeon)):
            for x in range(len(dungeon[y])):
                if dungeon[y][x] == " ":
                    self.tiles[x][y] = Tiles.FLOOR

    def decide_tile_types(self):
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                # We only care about walls right now
                if self.tiles[x][y] == Tiles.WALL:
                    neighbor_weights = ""
                    for j in [-1, 0, 1]:
                        for i in [-1, 0, 1]:
                            if i == 0 and j == 0:
                                continue
                            xx = x+i
                            yy = y+j
                            if 0 <= xx < self.size[0] and 0 <= yy < self.size[1]:
                                neighbor_weights += str(
                                    self.tiles[xx][yy])
                            else:
                                neighbor_weights += "1"
                    self.final_tiles[x][y] = self.tile_images[int(
                        neighbor_weights[::-1], 2)]
                else:
                    self.final_tiles[x][y] = self.tile_images[256]

    def draw_tiles(self):
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                c_sprite = pygame.sprite.Sprite(self.tiles_group)
                c_sprite.image = self.final_tiles[x][y]
                c_sprite.rect = pygame.rect.Rect(x*16, y*16, 16, 16)

    def tunnel_between(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> Iterator[tuple[int, int]]:
        """Return an L-shaped tunnel between these two points."""
        x1, y1 = start
        x2, y2 = end
        if random.random() < 0.5:  # 50% chance.
            # Move horizontally, then vertically.
            corner_x, corner_y = x2, y1
        else:
            # Move vertically, then horizontally.
            corner_x, corner_y = x1, y2

        # Generate the coordinates for this tunnel.
        for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
            yield x, y
        for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
            yield x, y

    def generate_dungeon(self):
        room_min_size = 3
        room_max_size = 6
        max_rooms = 50
        for _ in range(max_rooms):
            room_width = random.randint(room_min_size, room_max_size)
            room_height = random.randint(room_min_size, room_max_size)

            x = random.randint(1, self.size[0] - room_width - 1)
            y = random.randint(1, self.size[1] - room_height - 1)

            new_room = RectangularRoom(x, y, room_width, room_height)
            if any(new_room.intersects(other_room) for other_room in self.rooms):
                continue

            new_room.block(self.tiles)

            if len(self.rooms) == 0:
                # The first room, where the player starts.
                print(new_room.center)
                self.player_position = (
                    new_room.center[0]*16, new_room.center[1]*16)
            else:  # All rooms after the first.
                # Dig out a tunnel between this room and the previous one.
                for x, y in self.tunnel_between(self.rooms[-1].center, new_room.center):
                    self.tiles[x, y] = Tiles.FLOOR

            self.rooms.append(new_room)


class Game:
    def __init__(self):
        pygame.init()
        self.screen_size = pygame.Vector2(640, 320)
        self.tilemap_size = (16, 16)
        self.screen_tile_size = (40, 20)

        self.screen = pygame.display.set_mode(
            self.screen_size, flags=pygame.SCALED, vsync=0)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0  # todo

        self.tilemap = TileMap(self.screen_tile_size)

        self.player_group = pygame.sprite.Group()
        self.object = Player(self.player_group, self.tilemap.player_position)

        self.debug = True

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
            # self.player_group.draw(self.screen)
            self.screen.blit(self.object.image,
                             self.object.rect.topleft - pygame.Vector2(0, 16))

            if self.debug:
                pygame.draw.rect(self.screen, (0, 255, 0), self.object.rect, 1)
                for room in self.tilemap.rooms:
                    pygame.draw.rect(self.screen, (255, 0, 0), pygame.rect.Rect(
                        room.x1 * 16, room.y1 * 16, (room.x2 - room.x1)*16, (room.y2-room.y1)*16), 1)
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
