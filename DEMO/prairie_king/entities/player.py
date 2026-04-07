import pygame
from ..constants import TILESIZE

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        self.obstacle_sprites = obstacle_sprites
        self.direction = pygame.math.Vector2()
        self.speed = 5

        try:
            original_image = pygame.image.load('assets/cowboy_idle.png').convert_alpha()
            self.image = pygame.transform.scale_by(original_image, 4)
        except Exception:
            pass

        self.rect = self.image.get_rect(topleft=pos)

    def set_direction(self, dx: int, dy: int):
        self.direction.x = float(dx)
        self.direction.y = float(dy)

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        self.rect.x += int(self.direction.x * speed)
        self._collision('horizontal')
        self.rect.y += int(self.direction.y * speed)
        self._collision('vertical')

    def _collision(self, direction):
        for sprite in self.obstacle_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.rect.right = sprite.rect.left
                    if self.direction.x < 0: self.rect.left = sprite.rect.right
                if direction == 'vertical':
                    if self.direction.y > 0: self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0: self.rect.top = sprite.rect.bottom

    def update(self):
        self.move(self.speed)