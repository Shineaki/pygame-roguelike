import pygame


class HealthBar(pygame.sprite.Sprite):
    def __init__(self, group: pygame.sprite.Group, position: pygame.rect.Rect, offset: pygame.Vector2):
        super().__init__(group)
        self.image = pygame.surface.Surface(position.size)
        self.offset = offset
        pygame.draw.rect(self.image, (0, 200, 0), (0, 0, position.width, position.height))
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, position.width, position.height), 1)
        # innerPos  = (position[0]+1, position[1]+1)
        # innerSize = (int((size[0]-2) * progress), size[1]-2)
        # pygame.draw.rect(surface, color_health, (*innerPos, *innerSize))
        self.update_based_on_parent_pos(position)

    def update_based_on_parent_pos(self, position: pygame.Vector2):
        self.rect = (position.x + self.offset.x, position.y + self.offset.y)
