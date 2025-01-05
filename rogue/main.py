import pygame

from rogue.enums import AIRoundState, Direction
from rogue.map import TileMap
from rogue.player import Player


class Game:
    def __init__(self):
        pygame.init()
        self.screen_size = pygame.Vector2(640, 320)
        self.tilemap_size = (16, 16)
        self.screen_tile_size = (40, 20)

        self.screen = pygame.display.set_mode(
            self.screen_size, flags=pygame.SCALED, vsync=1)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0

        self.waiting_to_finish_movement = False

        self.player_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()

        self.tilemap = TileMap(self.screen_tile_size, self.enemy_group)

        self.player = Player(self.player_group, self.tilemap.player_position, self.tilemap)

        self.tilemap.init_with_player(self.player)

        self.camera_position = pygame.Vector2(self.screen.width / 2 - self.player.float_position.x,
                                              self.screen.height / 2 - self.player.float_position.y)

        self.debug = False
        self.tilemap.update_fov(self.player)

    def render_screen(self):
        # fill the screen with a color to wipe away anything from last frame
        self.screen.fill((13, 13, 13))
        draw_surf = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        self.player_group.update(self.dt)
        self.tilemap.update_fov(self.player)
        self.tilemap.tiles_group.update(self.tilemap.tilemap_states)
        self.tilemap.tiles_group.draw(draw_surf)
        self.enemy_group.update(self.dt, self.tilemap.tilemap_states)
        self.enemy_group.draw(draw_surf)
        # self.player_group.draw(self.screen)

        if self.debug:
            for ent in self.tilemap.entities:
                pygame.draw.rect(draw_surf,
                                 pygame.color.Color(0, 255, 0, 50),
                                 ent.rect, 1)
            for room in self.tilemap.rooms:
                pygame.draw.rect(draw_surf,
                                 (255, 0, 0, 50),
                                 pygame.rect.Rect(room.x1 * 16, room.y1 * 16,
                                                  (room.x2 - room.x1)*16,
                                                  (room.y2-room.y1)*16),
                                 1)
        self.camera_position = pygame.Vector2(self.screen.width / 2 - self.player.rect.x,
                                              self.screen.height / 2 - self.player.rect.y)
        self.screen.blit(draw_surf, self.camera_position)
        self.screen.blit(self.player.image, (self.screen.width / 2, self.screen.height / 2 - 16))

        # self.screen.blit(self.player.image, self.player.rect.topleft - pygame.Vector2(0, 16))
        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        keys = pygame.key.get_pressed()
        player_movement_direction = Direction.NULL
        if keys[pygame.K_d]:
            player_movement_direction = Direction.RIGHT
        if keys[pygame.K_a]:
            player_movement_direction = Direction.LEFT
        if keys[pygame.K_s]:
            player_movement_direction = Direction.DOWN
        if keys[pygame.K_w]:
            player_movement_direction = Direction.UP

        return self.player.move(player_movement_direction)

    def enemy_turn(self, player_moved: bool):
        if player_moved:
            # Order enemies by distance to player
            self.tilemap.enemies = sorted(self.tilemap.enemies, key=lambda x: x.simple_distance_to(self.player))
            # If player moved and movement finished -> Move minions
            for enemy in self.tilemap.enemies:
                enemy.move()
            return True
        return False

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000

            if self.waiting_to_finish_movement:
                finished = all([en.round_state == AIRoundState.DONE for en in self.tilemap.enemies])
                if finished:
                    self.waiting_to_finish_movement = False
            else:
                player_moved = self.handle_input()
                enemies_moved = self.enemy_turn(player_moved)

                if player_moved and enemies_moved:
                    self.waiting_to_finish_movement = True

            # Handle player input
            # Move creeps
            # Render screen
            self.render_screen()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
