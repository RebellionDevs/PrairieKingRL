import pygame
from map import get_map
from settings import TILESIZE
from tile import Tile
from player import Player

class Level:
    def __init__(self):

        self.display_surface = pygame.display.get_surface()
        
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()

        self.create_map(1)

    def create_map(self, index):
        self.map = get_map(index)

        for row_index, row in enumerate(self.map):
            for col_index, col in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE

                if col == 1: Tile((x, y), [self.visible_sprites, self.obstacle_sprites])
                if col == 99: self.player = Player((x, y), [self.visible_sprites], self.obstacle_sprites)

    def run(self):
        self.visible_sprites.draw(self.display_surface)
        self.visible_sprites.update()