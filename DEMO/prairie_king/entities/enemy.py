import pygame
import random
import math
from ..constants import TILESIZE, WIDTH, HEIGHT

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, enemy_type: int = 0, obstacle_sprites=None, on_death=None):
        super().__init__(groups)
        self.player = player
        self.all_enemies = groups[1] 
        self.obstacle_sprites = obstacle_sprites or pygame.sprite.Group()
        self.on_death = on_death
        self.type = enemy_type
        self.deployed = False

        self._setup_stats()
        self._setup_visual()

        self.rect = self.image.get_rect(center=pos)
        self.speed = self.base_speed
        self.direction = pygame.math.Vector2(0, 0)
        self.flash_timer = 0

        if self.type == 6:
            self._pick_deployment_target()

    def _setup_stats(self):
        if self.type == 0:
            self.base_speed = 1.8
            self.health = 1
        else:
            self.base_speed = 4
            self.health = 2

    def _setup_visual(self):
        try:
            filename = 'assets/spikey.png' if self.type == 6 else 'assets/enemy.png'
            img = pygame.image.load(filename).convert_alpha()
            if self.type == 6:
                self.image = pygame.transform.scale_by(img, 1.3)
            else:
                self.image = pygame.transform.scale_by(img, 4)
        except (FileNotFoundError, pygame.error):
            color = (200, 50, 50) if self.type == 0 else (100, 220, 100)
            self.image = pygame.Surface((TILESIZE, TILESIZE))
            self.image.fill(color)

    def take_damage(self, amount: int = 1):
        self.health -= amount
        if self.health <= 0:
            if self.on_death:
                self.on_death(self.rect.center)
            self.kill()
            return True
        return False

    def update(self):
        if self.flash_timer > 0:
            self.flash_timer -= 1

        if self.type == 6:
            self._update_spikey()
        else:
            self._update_standard()
            
        if not self.deployed:
            self._apply_separation()

    def _move_and_avoid(self, target_pos):
        target_vec = pygame.math.Vector2(target_pos[0] - self.rect.centerx, 
                                        target_pos[1] - self.rect.centery)
        dist = target_vec.length()
        
        if dist < 5:
            return dist

        target_vec = target_vec.normalize()
        angles = [0, 45, -45, 90, -90]
        
        for angle in angles:
            test_dir = target_vec.rotate(angle)
            new_center = (
                self.rect.centerx + test_dir.x * self.speed,
                self.rect.centery + test_dir.y * self.speed
            )
            
            test_rect = self.rect.copy()
            test_rect.center = new_center

            if not self._is_colliding_obstacles(test_rect):
                self.rect.center = new_center
                break
        
        return dist

    def _apply_separation(self):
        separation_vec = pygame.math.Vector2(0, 0)
        neighbor_dist = TILESIZE * 0.95
        
        for enemy in self.all_enemies:
            if enemy == self:
                continue
            
            diff = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(enemy.rect.center)
            dist = diff.length()
            
            if 0 < dist < neighbor_dist:
                separation_vec += diff.normalize() * (neighbor_dist - dist) * 0.15

        if separation_vec.length() > 0:
            new_rect = self.rect.copy()
            new_rect.centerx += int(separation_vec.x)
            new_rect.centery += int(separation_vec.y)
            
            if not self._is_colliding_obstacles(new_rect):
                self.rect.center = new_rect.center

    def _update_standard(self):
        if not self.player:
            return
        self._move_and_avoid(self.player.rect.center)

    def _update_spikey(self):
        if self.deployed:
            return
        dist = self._move_and_avoid(self.target_position)
        if dist < 20:
            self.deployed = True
            self.speed = 0
            self.health += 5
            self._create_deployed_visual()

    def _is_colliding_obstacles(self, test_rect):
        for obstacle in self.obstacle_sprites:
            if obstacle.rect.colliderect(test_rect):
                return True
        return False

    def _pick_deployment_target(self):
        attempts = 0
        while attempts < 50:
            target = (random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100))
            temp_rect = self.rect.copy()
            temp_rect.center = target
            if not self._is_colliding_obstacles(temp_rect.inflate(20, 20)):
                self.target_position = target
                return
            attempts += 1
        self.target_position = (WIDTH // 2, HEIGHT // 2)

    def _create_deployed_visual(self):
        try:
            img = pygame.image.load('assets/spikey_deployed.png').convert_alpha()
            self.image = pygame.transform.scale_by(img, 1.3)
        except:
            pass

    def draw(self, surface):
        surface.blit(self.image, self.rect)