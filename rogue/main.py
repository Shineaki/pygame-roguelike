import random
from os.path import join
from typing import TYPE_CHECKING, Iterator, Optional

import numpy as np
import pygame
import tcod
from tcod.map import compute_fov

from rogue.enemy import Enemy
from rogue.enums import IntTiles, Tiles, TileState
from rogue.player import Player
from rogue.rect_room import RectangularRoom
from rogue.tile import Tile


class TilesGroup(pygame.sprite.Group):
    def draw(self, surface: pygame.surface.Surface):
        super().draw(surface=surface)


class TileMap:
    def __init__(self, size: tuple[int], enemy_group: pygame.sprite.Group):
        self.player_ref = None
        self.enemy_group = enemy_group

        self.size = size
        self.player_position = (0, 0)
        self.tileset = pygame.image.load(
            join("resources", "tiles", "ff.png")).convert_alpha()

        self.tile_images = {
            i: self.create_tile_image(i) for i in range(256+1)
        }

        self.all_tiles = np.full(size, fill_value=IntTiles.WALL, order="F")
        self.final_tiles = np.full(size, fill_value=Tiles.FLOOR, order="F")
        self.visible_tiles = np.full(size, fill_value=False, order="F")
        self.explored_tiles = np.full(size, fill_value=False, order="F")
        self.rooms: list[RectangularRoom] = []
        self.enemies: list[Enemy] = []
        self.tiles_group = TilesGroup()
        self.tilemap_states = np.full(
            size, fill_value=TileState.UNEXPLORED, order="F")

        self.entities = []

        self.generate_dungeon()
        self.decide_tile_types()
        self.create_tiles()

    def init_with_player(self, player_ref):
        self.player_ref = player_ref
        self.generate_enemies(self.enemy_group)

        self.entities.append(player_ref)

    def update_fov(self, player: Player) -> None:
        """Recompute the visible area based on the players point of view."""
        self.visible_tiles[:] = compute_fov(
            self.all_tiles,
            (player.rect.x//16, player.rect.y//16),
            radius=4,
        )
        # If a tile is "visible" it should be added to "explored".
        self.explored_tiles |= self.visible_tiles

        self.tilemap_states[:] = (self.explored_tiles.astype(
            int) + self.visible_tiles.astype(int))

    def create_tile_image(self, idx: int) -> pygame.Surface:
        tmp_surface = pygame.Surface((16, 16))
        x = idx % 24
        y = idx // 24
        tmp_surface.blit(self.tileset, (0, 0), (x * 16, y * 16, 16, 16))
        return tmp_surface

    def decide_tile_types(self):
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                # We only care about walls right now
                if self.all_tiles[x][y] == IntTiles.WALL:
                    neighbor_weights = ""
                    for j in [-1, 0, 1]:
                        for i in [-1, 0, 1]:
                            if i == 0 and j == 0:
                                continue
                            xx = x+i
                            yy = y+j
                            if 0 <= xx < self.size[0] and 0 <= yy < self.size[1]:
                                neighbor_weights += {
                                    "0": "1",
                                    "1": "0"
                                }[str(self.all_tiles[xx][yy])]
                            else:
                                neighbor_weights += "1"
                    self.final_tiles[x][y] = self.tile_images[int(
                        neighbor_weights[::-1], 2)]
                else:
                    self.final_tiles[x][y] = self.tile_images[256]

    def create_tiles(self):
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                Tile(self.tiles_group, self.final_tiles[x][y],
                     pygame.rect.Rect(x*16, y*16, 16, 16)
                     )

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

    def generate_enemies(self, enemy_group: pygame.sprite.Group):
        for c_room in self.rooms:
            x = random.randint(c_room.x1, c_room.x2 - 1)
            y = random.randint(c_room.y1, c_room.y2 - 1)

            if any(enemy.rect.x // 16 == x and enemy.rect.y // 16 == y for enemy in self.enemies):
                continue

            c_enemy = Enemy(enemy_group, (x*16, y*16), self, self.player_ref)
            self.enemies.append(c_enemy)
            self.entities.append(c_enemy)

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

            new_room.block(self.all_tiles)

            if len(self.rooms) == 0:
                # The first room, where the player starts.
                self.player_position = (
                    new_room.center[0]*16, new_room.center[1]*16)
            else:  # All rooms after the first.
                # Dig out a tunnel between this room and the previous one.
                for x, y in self.tunnel_between(self.rooms[-1].center, new_room.center):
                    self.all_tiles[x, y] = Tiles.FLOOR.value

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

        self.player_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()

        self.tilemap = TileMap(self.screen_tile_size, self.enemy_group)

        self.player = Player(
            self.player_group, self.tilemap.player_position, self.tilemap)

        self.tilemap.init_with_player(self.player)

        self.debug = False
        self.tilemap.update_fov(self.player)

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # fill the screen with a color to wipe away anything from last frame
            self.screen.fill("black")

            self.player_group.update(self.dt)
            self.tilemap.update_fov(self.player)
            self.tilemap.tiles_group.update(self.tilemap.tilemap_states)
            self.tilemap.tiles_group.draw(self.screen)
            draw_surf = pygame.Surface(self.screen_size, pygame.SRCALPHA)
            self.enemy_group.update(self.dt, self.tilemap.tilemap_states)
            self.enemy_group.draw(self.screen)
            # self.player_group.draw(self.screen)
            self.screen.blit(self.player.image,
                             self.player.rect.topleft - pygame.Vector2(0, 16))
            if self.debug:
                pygame.draw.rect(draw_surf, pygame.color.Color(0, 255, 0, 50),
                                 self.player.rect, 1)
                for room in self.tilemap.rooms:
                    pygame.draw.rect(draw_surf, (255, 0, 0, 50), pygame.rect.Rect(
                        room.x1 * 16, room.y1 * 16, (room.x2 - room.x1)*16, (room.y2-room.y1)*16), 1)
            self.screen.blit(draw_surf, (0, 0))
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
