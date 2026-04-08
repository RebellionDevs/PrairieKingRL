import pygame
from ..constants import TILESIZE

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, tile_type: int, render_mode=None):
        super().__init__(groups)
        self.tile_type = tile_type
        if render_mode == "human":
            self.image = self._load_image(tile_type)
            self.rect = self.image.get_rect(topleft=pos)
        else:
            self.rect = pygame.Rect(pos[0], pos[1], TILESIZE, TILESIZE)

    def _load_image(self, tile_type: int) -> pygame.Surface:
        try:
            if tile_type == 1:
                img = pygame.image.load('assets/bush1.png').convert_alpha()
            elif tile_type == 2:
                img = pygame.image.load('assets/floor_de1.png').convert_alpha()
            elif tile_type == 4:
                img = pygame.image.load('assets/floor_de2.png').convert_alpha()
            elif tile_type == 0:
                img = pygame.image.load('assets/floor_de4.png').convert_alpha()
            elif tile_type == 6:
                img = pygame.image.load('assets/logs.png').convert_alpha()
            else:
                img = pygame.image.load('assets/floor_de4.png').convert_alpha()
            return pygame.transform.scale(img, (TILESIZE, TILESIZE))
        except Exception:
            img = pygame.Surface((TILESIZE, TILESIZE))
            img.fill((80, 80, 80))
            return img