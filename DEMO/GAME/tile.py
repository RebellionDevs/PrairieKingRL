import pygame
from settings import TILESIZE

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        original_image = pygame.image.load('assets/images/bush1.png').convert_alpha()
        self.image = pygame.transform.scale_by(original_image, 4)

        self.rect = self.image.get_rect(topleft=pos)