import pygame
from .maps import get_map
from .constants import TILESIZE, WIDTH, HEIGHT
from .entities.tile import Tile
from .entities.player import Player


class World:
    def __init__(self):
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()

        # self.bullet_sprites = pygame.sprite.Group()
        # self.enemy_sprites = pygame.sprite.Group()

        self.player = None
        self.map_data = None
        self.reset(level=1)

    def reset(self, level: int = 1):
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.create_map(level)

    def create_map(self, index: int):
        self.map_data = get_map(index)

        for row_index, row in enumerate(self.map_data):
            for col_index, tile_type in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE

                if tile_type == 99:                     
                    self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites)

                else:
                    tile = Tile((x, y), [self.visible_sprites], tile_type)

                    if tile_type == 1:
                        self.obstacle_sprites.add(tile)

    def step(self, action: int):
        dirs = {0: (0, 0), 1: (0, -1), 2: (0, 1), 3: (-1, 0), 4: (1, 0)}
        dx, dy = dirs.get(action, (0, 0))

        if self.player:
            self.player.set_direction(dx, dy)
            self.player.update()

    def render(self, surface=None):
        if surface is None:
            return

        surface.fill('black')
        self.visible_sprites.draw(surface)

    def set_surface(self, surface):
        self.display_surface = surface