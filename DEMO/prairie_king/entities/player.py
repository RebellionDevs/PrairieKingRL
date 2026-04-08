import pygame
from ..constants import TILESIZE, WIDTH, HEIGHT

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, render_mode=None):
        super().__init__(groups)
        self.obstacle_sprites = obstacle_sprites
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.alive = True

        if render_mode == "human":
            try:
                original_image = pygame.image.load('assets/cowboy_idle.png').convert_alpha()
                self.image = pygame.transform.scale_by(original_image, 4)
            except Exception:
                self.image = pygame.Surface((TILESIZE, TILESIZE))
                self.image.fill((200, 200, 50))
            self.rect = self.image.get_rect(topleft=pos)
        else:
            self.rect = pygame.Rect(pos[0], pos[1], TILESIZE, TILESIZE)

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

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)

    def _collision(self, direction):
        for sprite in self.obstacle_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.rect.left = sprite.rect.right
                if direction == 'vertical':
                    if self.direction.y > 0:
                        self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.rect.top = sprite.rect.bottom

    def take_damage(self):
        self.alive = False

    def update(self):
        if self.alive:
            self.move(self.speed)