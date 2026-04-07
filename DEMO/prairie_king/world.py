import pygame
from .maps import get_map
from .constants import TILESIZE, WIDTH, HEIGHT
from .entities.tile import Tile
from .entities.player import Player
from .entities.bullet import Bullet


class World:
    def __init__(self):
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()

        self.player = None
        self.shoot_cooldown = 0
        self.shoot_rate = 26

        self.map_data = None
        self.reset(2)

    def reset(self, level):
        self.shoot_cooldown = 0
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.create_map(level)

    def create_map(self, index: int):
        self.map_data = get_map(index)
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()

        for row_index, row in enumerate(self.map_data):
            for col_index, tile_type in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE

                tile = Tile((x, y), [self.visible_sprites], tile_type)
                if tile_type == 1 or tile_type == 6:
                    self.obstacle_sprites.add(tile)

        center_x = (WIDTH // 2) - (TILESIZE // 2)
        center_y = (HEIGHT // 2) - (TILESIZE // 2)

        self.player = Player((center_x, center_y), [self.visible_sprites], self.obstacle_sprites)

    def shoot(self, direction):
        if not self.player or self.shoot_cooldown > 0: 
            return

        offset = (direction[0] * 28, direction[1] * 28)
        spawn_pos = (
            self.player.rect.centerx + offset[0],
            self.player.rect.centery + offset[1]
        )

        Bullet(spawn_pos, direction, [self.visible_sprites, self.bullet_sprites], self.obstacle_sprites)

        self.shoot_cooldown = self.shoot_rate


    def step(self, action: int):
        dirs = {
            0: (0, 0),
            1: (0, -1),
            2: (0, 1),
            3: (-1, 0),
            4: (1, 0),
            5: (-1, -1),
            6: (1, -1),
            7: (-1, 1),
            8: (1, 1),
        }
        dx, dy = dirs.get(action, (0, 0))

        if self.player:
            self.player.set_direction(dx, dy)
            self.player.update()

        self.bullet_sprites.update()

        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1

    def render(self, surface=None):
        if surface is None:
            return
        surface.fill('black')

        for sprite in self.visible_sprites:
            if not isinstance(sprite, Player):
                surface.blit(sprite.image, sprite.rect)

        if self.player:
            surface.blit(self.player.image, self.player.rect)

    def set_surface(self, surface):
        self.display_surface = surface