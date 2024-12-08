from os.path import join

import pygame

from rogue.player import Player


class TileMap:
    def __init__(self, size: tuple[int]):
        self.images = {
            "wall": pygame.image.load(join("resources", "tiles", "wall_mid.png")).convert_alpha(),
            "floor": pygame.image.load(join("resources", "tiles", "floor_1.png")).convert_alpha()
        }
        self.sprites = []
        self.tiles_group = pygame.sprite.Group()
        for x in range(size[0]):
            for y in range(size[1]):
                c_sprite = pygame.sprite.Sprite(self.tiles_group)
                if y == 0 or y == size[1]-1:
                    c_sprite.image = self.images["wall"]
                else:
                    c_sprite.image = self.images["floor"]
                c_sprite.rect = pygame.rect.Rect(x*16, 20+y*16, 16, 16)


class Game:
    def __init__(self):
        pygame.init()
        self.screen_size = pygame.Vector2(640, 360)
        self.tilemap_size = (16, 16)
        self.screen_tile_size = (40, 20)

        self.screen = pygame.display.set_mode(
            (640, 360), flags=pygame.SCALED, vsync=0)
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
