import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, tile_type):
        super().__init__(groups)
        self.image = self._load_image(tile_type)
        self.rect = self.image.get_rect(topleft=pos)

    def _load_image(self, tile_type):
        if tile_type == 1: 
            img = pygame.image.load('../../assets/bush1.png').convert_alpha()
        elif tile_type == 2: 
            img = pygame.image.load('../../assets/floor_de1.png').convert_alpha()
        elif tile_type == 4: 
            img = pygame.image.load('../../assets/floor_de2.png').convert_alpha()
        elif tile_type == 0: 
            img = pygame.image.load('../../assets/floor_de4.png').convert_alpha()
        elif tile_type == 6: 
            img = pygame.image.load('../../assets/logs.png').convert_alpha()

        return pygame.transform.scale_by(img, 4)