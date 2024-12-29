from enum import Enum
from os.path import join
from typing import TYPE_CHECKING, List, Tuple

import numpy as np
import pygame
import tcod

from rogue.enums import AnimState, IntTiles, TileState

# from rogue.main import TileMap
# from rogue.player import Player


class AIRoundState(Enum):
    DONE = 0
    MOVING = 1


class AIState(Enum):
    IDLE = 0
    CHASING = 1


class Enemy(pygame.sprite.Sprite):
    def __init__(self, group: pygame.sprite.Group, starting_pos: tuple[int, int], map_ref, player_ref):
        super().__init__(group)

        self.position = pygame.Vector2(starting_pos[0], starting_pos[1])

        self.blocks_movement = True

        self.target_position = None

        self.map_ref = map_ref
        self.player_ref = player_ref

        # Animation
        self.anim_len = 4
        self.anim_idx = 0
        self.images = {
            AnimState.IDLE: [pygame.image.load(
                join("resources", "enemies", "red", "idle", f"enemy_idle{i+1}.png")).convert_alpha() for i in range(self.anim_len)],
            AnimState.RUN: [pygame.image.load(
                join("resources", "enemies", "red", "run", f"enemy_run{i+1}.png")).convert_alpha() for i in range(self.anim_len)]
        }
        self.c_anim_state = AnimState.IDLE
        self.anim_timer = 0
        self.image = self.images[self.c_anim_state][self.anim_idx]
        self.rect = pygame.rect.Rect(starting_pos, (16, 16))

        # AI
        self.ai_state = AIState.IDLE
        self.round_state = AIRoundState.DONE

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.
        cost = np.array(
            self.map_ref.all_tiles, dtype=np.int8)

        for entity in self.map_ref.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.rect.x // 16, entity.rect.y // 16]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[entity.rect.x//16, entity.rect.y//16] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=0)
        pathfinder = tcod.path.Pathfinder(graph)

        # Start position.
        pathfinder.add_root((self.rect.x//16, self.rect.y//16))

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[
            1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]

    def update_state(self):
        if self.ai_state == AIState.IDLE:
            visible = self.map_ref.tilemap_states[self.rect.x //
                                                  16][self.rect.y//16]
            if visible == TileState.VISIBLE:
                self.ai_state = AIState.CHASING
            else:
                return
        if self.round_state == AIRoundState.MOVING:
            return
        # if self.round_state == AIRoundState.DONE:
        #     return

        path = self.get_path_to(self.player_ref.rect.x //
                                16, self.player_ref.rect.y // 16)
        if path:
            self.target_position = (path[0][0]*16, path[0][1]*16)
        else:
            self.target_position = None

    def update(self, dt: float, map_state: np.array):
        # self.update_state()
        if self.target_position and self.target_position != (self.rect.x, self.rect.y):
            self.round_state = AIRoundState.MOVING
            pos = pygame.Vector2(
                self.rect.x - self.target_position[0], self.rect.y - self.target_position[1])
            pos = pos.normalize()
            self.position -= pos * 40 * dt
            self.rect.x = self.position.x
            self.rect.y = self.position.y
        if self.target_position == (self.rect.x, self.rect.y):
            self.round_state = AIRoundState.DONE
            self.target_position = None
        self.anim_timer += dt
        if self.anim_timer >= 0.08:
            self.anim_timer = 0.0
            self.anim_idx = (self.anim_idx + 1) % self.anim_len
        self.image = self.images[self.c_anim_state][self.anim_idx]

        if map_state[self.rect.x // 16][self.rect.y // 16] != TileState.VISIBLE:
            self.image = pygame.Surface((0, 0))
