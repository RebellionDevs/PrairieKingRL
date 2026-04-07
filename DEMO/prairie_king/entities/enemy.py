import pygame
import random
from ..constants import TILESIZE, WIDTH, HEIGHT

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, enemy_type: int = 0, obstacle_sprites=None):
        super().__init__(groups)
        self.player = player
        self.obstacle_sprites = obstacle_sprites or pygame.sprite.Group()
        self.type = enemy_type
        self.alive = True
        self.deployed = False

        self._setup_stats()
        self._setup_visual()

        self.rect = self.image.get_rect(center=pos)

        self.speed = self.base_speed
        self.direction = pygame.math.Vector2(0, 0)

        if self.type == 6:
            self._pick_deployment_target()

        self.flash_timer = 0

    def _setup_stats(self):
        if self.type == 0:
            self.base_speed = random.uniform(1.4, 2.7)
            self.health = random.randint(1, 3)
        else:
            self.base_speed = 5
            self.health = 2
            self.deployed = False

    def _setup_visual(self):
        try:
            if self.type == 6:
                img = pygame.image.load('assets/spikey.png').convert_alpha()
            else:
                img = pygame.image.load('assets/enemy.png').convert_alpha()
            self.image = pygame.transform.scale_by(img, 3)
        except (FileNotFoundError, pygame.error):
            color = (200, 50, 50) if self.type == 0 else (100, 220, 100)
            self.image = pygame.Surface((TILESIZE, TILESIZE))
            self.image.fill(color)

    def _pick_deployment_target(self):
        self.target_position = (
            random.randint(100, WIDTH - 100),
            random.randint(100, HEIGHT - 100)
        )

    def take_damage(self, amount: int = 1):
        self.health -= amount
        self.flash_timer = 120

        if self.health <= 0:
            self.kill()
            return True
        return False

    def update(self):
        if not self.alive:
            return

        if self.flash_timer > 0:
            self.flash_timer -= 1

        if self.type == 6:
            self._update_spikey()
        else:
            self._update_standard()

    def _update_standard(self):
        if not self.player:
            return

        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = (dx**2 + dy**2)**0.5 or 1.0

        self.direction.x = dx / dist
        self.direction.y = dy / dist

        new_rect = self.rect.copy()
        new_rect.x += int(self.direction.x * self.speed)
        new_rect.y += int(self.direction.y * self.speed)

        if not self._is_colliding(new_rect):
            self.rect = new_rect

    def _update_spikey(self):
        if self.deployed:
            return

        if not hasattr(self, 'target_position'):
            self._pick_deployment_target()

        dx = self.target_position[0] - self.rect.centerx
        dy = self.target_position[1] - self.rect.centery
        dist = (dx**2 + dy**2)**0.5 or 1.0

        if dist < 25:
            self.deployed = True
            self.speed = 0
            self.health += 5
            self._create_deployed_visual()
            return

        self.direction.x = dx / dist
        self.direction.y = dy / dist

        new_rect = self.rect.copy()
        new_rect.x += int(self.direction.x * self.speed)
        new_rect.y += int(self.direction.y * self.speed)

        if not self._is_colliding(new_rect):
            self.rect = new_rect

    def _is_colliding(self, test_rect):
        for obstacle in self.obstacle_sprites:
            if test_rect.colliderect(obstacle.rect):
                return True

        for sprite in self.groups()[0]:
            if sprite != self and isinstance(sprite, Enemy):
                if test_rect.colliderect(sprite.rect):
                    return True
        return False

    def _create_deployed_visual(self):
        try:
            img = pygame.image.load('assets/spikey_deployed.png').convert_alpha()
            self.image = pygame.transform.scale_by(img, 3)
        except:
            self.image = pygame.transform.scale(self.image, (int(TILESIZE * 1.3), int(TILESIZE * 1.3)))

    def draw(self, surface):
        if self.flash_timer > 0:
            temp = self.image.copy()
            temp.fill((255, 100, 100), special_flags=pygame.BLEND_ADD)
            surface.blit(temp, self.rect)
        else:
            surface.blit(self.image, self.rect)