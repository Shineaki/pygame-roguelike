import copy
from typing import Optional

import pygame

from rogue.enums import TileState


class Tile(pygame.sprite.Sprite):
    def __init__(self, group: Optional[pygame.sprite.Group], image: Optional[pygame.surface.Surface], rect: Optional[pygame.rect.Rect]):
        super().__init__(group)
        self.image_dict = {
            TileState.UNEXPLORED: pygame.Surface(rect.size),
            TileState.EXPLORED: image.copy(),
            TileState.VISIBLE: image,
        }
        pygame.draw.rect(self.image_dict[TileState.UNEXPLORED],
                         (13, 13, 13), pygame.rect.Rect(0, 0, 16, 16))
        self.image_dict[TileState.EXPLORED].set_alpha(100)
        self.rect = rect
        self.state = TileState.UNEXPLORED

    def update(self, tilemap_state):
        self.state = tilemap_state[self.rect.x // 16][self.rect.y // 16]
        self.image = self.image_dict[self.state]
