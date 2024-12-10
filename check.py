import pygame

screen = pygame.surface.Surface((384, 176))

with open("missing.txt", "w") as outfile:
    for i in range(256):
        c_image = pygame.surface.Surface((16, 16))
        indexes = [(1, 1), (6, 1), (11, 1), (1, 6),
                   (11, 6), (1, 11), (6, 11), (11, 11), ]
        indexes = [pygame.rect.Rect(i[0], i[1], 4, 4)
                   for i in indexes]
        for idx, ch in enumerate(f"{i:08b}"[::-1]):
            if ch == "1":
                pygame.draw.rect(c_image, (255, 0, 0), indexes[idx], 4)
        pygame.draw.rect(c_image, (250, 250, 250),
                         pygame.rect.Rect(6, 6, 4, 4), 4)
        screen.blit(c_image, ((i % 24) * 16, (i//24) * 16), (0, 0, 16, 16))
pygame.image.save(screen, "ff.png")
