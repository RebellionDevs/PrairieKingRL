from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, surface):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=(pos[0] * TILE_SIZE, pos[1] * TILE_SIZE))
