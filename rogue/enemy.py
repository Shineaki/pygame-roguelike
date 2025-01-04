from os.path import join
from typing import List, Tuple

import numpy as np
import pygame
import tcod

from rogue.components.animator import Animator
from rogue.entity import Entity
from rogue.enums import AIRoundState, AIState, AnimState, Direction, TileState


class HealthBar(pygame.sprite.Sprite):
    def __init__(self, group: pygame.sprite.Group, pos):
        super().__init__(group)
        self.image = pygame.surface.Surface((16, 4))
        pygame.draw.rect(self.image, (0, 200, 0), (0, 0, 16, 4))
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, 16, 4), 1)
        # innerPos  = (position[0]+1, position[1]+1)
        # innerSize = (int((size[0]-2) * progress), size[1]-2)
        # pygame.draw.rect(surface, color_health, (*innerPos, *innerSize))
        self.rect = (pos[0], pos[1]-2)

    def update_based_on_parent_pos(self, pos):
        self.rect = (pos[0], pos[1]-2)


class Enemy(Entity):
    def __init__(self, group: pygame.sprite.Group, starting_pos: tuple[int, int], map_ref, player_ref):
        super().__init__(group=group,
                         blocks_movement=True,
                         starting_position=starting_pos)
        self.health_bar = HealthBar(group, pygame.rect.Rect(self.float_position, (16, 4)))
        self.animator = Animator(character_name="small_orc")

        self.target_position = None

        self.map_ref = map_ref
        self.player_ref = player_ref

        # Animation
        self.image = self.animator.get_current_image()
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
        pathfinder.add_root(self.tile_position)

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]

    def update_state(self):
        if self.ai_state == AIState.IDLE:
            visible = self.map_ref.tilemap_states[self.tile_position[0]][self.tile_position[1]]
            if visible == TileState.VISIBLE:
                self.ai_state = AIState.CHASING
            else:
                return
        if self.round_state == AIRoundState.MOVING:
            return
        # if self.round_state == AIRoundState.DONE:
        #     return

        path = self.get_path_to(self.player_ref.tile_position[0], self.player_ref.tile_position[1])
        if path:
            distance = self.simple_distance_to(self.player_ref)
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
        # Refactor this pile of garbage below (and above)
        # Fix animation jitter if continuously moving asd
        self.animator.update(dt)
        if self.target_position:
            direction = self.float_position - pygame.Vector2(self.target_position[0], self.target_position[1])
            if abs(direction.length()) > 1:
                self.round_state = AIRoundState.MOVING
                self.animator.update_state(AnimState.RUN)
                pos = pygame.Vector2(self.rect.x - self.target_position[0], self.rect.y - self.target_position[1])
                pos = pos.normalize()
                self.float_position -= pos * 40 * dt
                if pos.x > 0:  # Facing left
                    self.facing_direction = Direction.LEFT
                else:
                    self.facing_direction = Direction.RIGHT
            else:
                self.float_position = pygame.Vector2(self.target_position[0], self.target_position[1])
                self.round_state = AIRoundState.DONE
                self.animator.update_state(AnimState.IDLE)
                self.target_position = None
            self.rect.x = self.float_position.x
            self.rect.y = self.float_position.y
            self.health_bar.update_based_on_parent_pos(self.rect)

        if map_state[self.tile_position[0]][self.tile_position[1]] == TileState.VISIBLE:
            self.image = self.animator.get_current_image()
            # Flip if moving left
            if self.facing_direction == Direction.LEFT:
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.image = pygame.Surface((0, 0))

    def move(self):
        self.update_state()
