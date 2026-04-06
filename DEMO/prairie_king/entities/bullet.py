from ..constants import *
import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, groups, obstacle_sprites):
        super().__init__(groups)

        self.direction = pygame.math.Vector2(direction)
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        self.speed = 10
        self.obstacle_sprites = obstacle_sprites

        original_image = pygame.image.load('assets/bullet.png').convert_alpha()
        self.image = pygame.transform.scale_by(original_image, 2)
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.rect.x += int(self.direction.x * self.speed)
        self.rect.y += int(self.direction.y * self.speed)

        if pygame.sprite.spritecollideany(self, self.obstacle_sprites):
            self.kill()
            return
        
        if (self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT): 
            self.kill()

