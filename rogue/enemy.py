from os.path import join
from typing import List, Tuple

import numpy as np
import pygame
import tcod

from rogue.entity import Entity
from rogue.enums import AIRoundState, AIState, AnimState, Direction, TileState


class Enemy(Entity):
    def __init__(self, group: pygame.sprite.Group, starting_pos: tuple[int, int], map_ref, player_ref):
        super().__init__(group=group,
                         blocks_movement=True,
                         starting_position=starting_pos)

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
        self.rect = pygame.rect.Rect(self.float_position, (16, 16))

        # AI
        self.ai_state = AIState.IDLE
        self.round_state = AIRoundState.DONE

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.
        cost = np.array(self.map_ref.all_tiles, dtype=np.int8)

        for entity in self.map_ref.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.tile_position[0], entity.tile_position[1]]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[entity.tile_position[0], entity.tile_position[1]] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=0)
        pathfinder = tcod.path.Pathfinder(graph)

        # Start position.
        pathfinder.add_root((self.rect.x//16, self.rect.y//16))

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

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
            dx = self.player_ref.tile_position[0] - self.tile_position[0]
            dy = self.player_ref.tile_position[1] - self.tile_position[1]
            distance = abs(dx) + abs(dy)
            if distance == 1:
                print("Minion attacked you!")
            else:
                for en in self.map_ref.enemies:
                    if en.tile_position == (path[0][0], path[0][1]):
                        return
                self.target_position = (path[0][0]*16, path[0][1]*16)
                self.tile_position = (path[0][0], path[0][1])
        else:
            self.target_position = None

    def update(self, dt: float, map_state: np.array):
        # TODO List
        # If visible -> Animate
        # If chasing -> Move
        if self.target_position and self.target_position != (self.rect.x, self.rect.y):
            self.round_state = AIRoundState.MOVING
            pos = pygame.Vector2(
                self.rect.x - self.target_position[0], self.rect.y - self.target_position[1])
            pos = pos.normalize()
            self.float_position -= pos * 40 * dt
            self.rect.x = self.float_position.x
            self.rect.y = self.float_position.y
            if pos.x > 0:  # Facing left
                self.facing_direction = Direction.LEFT
            else:
                self.facing_direction = Direction.RIGHT

        # TODO:
        # Moving animation
        # Queue next animation
        # Animation is separate class
        # Merge with player

        # AI Refactor + Cleanup -> something is strange with the pathing

        if self.target_position == (self.rect.x, self.rect.y):
            self.round_state = AIRoundState.DONE
            self.target_position = None
        self.anim_timer += dt
        if self.anim_timer >= 0.08:
            self.anim_timer = 0.0
            self.anim_idx = (self.anim_idx + 1) % self.anim_len
        self.image = self.images[self.c_anim_state][self.anim_idx]

        if map_state[self.tile_position[0]][self.tile_position[1]] == TileState.VISIBLE:
            # Flip if moving left
            if self.facing_direction == Direction.LEFT:
                self.image = pygame.transform.flip(self.images[self.c_anim_state][self.anim_idx], True, False)
            else:
                self.images[self.c_anim_state][self.anim_idx]
        else:
            self.image = pygame.Surface((0, 0))

    def move(self):
        self.update_state()
