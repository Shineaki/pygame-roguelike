import pygame


class Tile(pygame.sprite.Sprite):
    def __init__(self, group, image, rect):
        super().__init__(group)
        self.image = image
        self.rect = rect
        # pygame.draw.rect(self.image, pygame.color.Color(
        #     255, 0, 0, 200), pygame.rect.Rect(0, 0, 16, 16))
