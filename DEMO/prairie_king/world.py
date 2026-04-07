import pygame
import random
from .maps import get_map
from .constants import TILESIZE, WIDTH, HEIGHT
from .entities.tile import Tile
from .entities.player import Player
from .entities.bullet import Bullet
from .entities.enemy import Enemy


class World:
    def __init__(self):
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        self.player = None
        self.current_level = 1
        self.current_wave = 1

        self.shoot_cooldown = 0
        self.shoot_rate = 22

        self.wave_timer = 0
        self.wave_duration = 5400
        self.spawn_timer = 0

        self.reset(level=1)

    def reset(self, level):
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()

        self.current_level = level
        self.current_wave = 1
        self.shoot_cooldown = 0
        self.wave_timer = 0
        self.spawn_timer = 180

        self.create_map(level)

    def create_map(self, index: int):
        self.map_data = get_map(index)

        for row_index, row in enumerate(self.map_data):
            for col_index, tile_type in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE

                if tile_type != 99:
                    tile = Tile((x, y), [self.visible_sprites], tile_type)

                    if tile_type in (1, 6):
                        self.obstacle_sprites.add(tile)

        center_x = (WIDTH // 2) - (TILESIZE // 2)
        center_y = (HEIGHT // 2) - (TILESIZE // 2)
        self.player = Player((center_x, center_y), [self.visible_sprites], self.obstacle_sprites)

    def step(self, move_action: int):
        if not self.player or not self.player.alive:
            return

        dirs = {0: (0, 0), 1: (0, -1), 2: (0, 1), 3: (-1, 0), 4: (1, 0),
                5: (-1, -1), 6: (1, -1), 7: (-1, 1), 8: (1, 1)}
        dx, dy = dirs.get(move_action, (0, 0))
        self.player.set_direction(dx, dy)
        self.player.update()

        self.bullet_sprites.update()
        self.enemy_sprites.update()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self.wave_timer += 1
        if self.spawn_timer > 0:
            self.spawn_timer -= 1

        if self.spawn_timer <= 0:
            self.spawn_wave()
            self.spawn_timer = 600

        hits = pygame.sprite.groupcollide(self.bullet_sprites, self.enemy_sprites, True, False)
        for bullet, enemies in hits.items():
            if enemies:
                enemies[0].take_damage(1)

        if pygame.sprite.spritecollideany(self.player, self.enemy_sprites):
            self.player.take_damage()

        if self.wave_timer >= self.wave_duration and len(self.enemy_sprites) == 0:
            self.reset(level=self.current_level + 1)

    def spawn_wave(self):
        spawn_points = self._get_spawn_points()
        if not spawn_points:
            return

        groups = self._group_by_side(spawn_points)

        for side, points in groups.items():
            clear_points = self._get_clear_points(points)
            if not clear_points:
                continue

            if self.current_level == 1:
                self._spawn_standard_group(clear_points)
            else:
                if random.random() < 0.15:
                    self._spawn_spikey(clear_points)
                else:
                    self._spawn_standard_group(clear_points)

    def _get_clear_points(self, points):
        clear = []
        for p in points:
            is_clear = True
            for enemy in self.enemy_sprites:
                if hasattr(enemy, 'rect'):
                    if abs(enemy.rect.centerx - p[0]) < TILESIZE and abs(enemy.rect.centery - p[1]) < TILESIZE:
                        is_clear = False
                        break
            if is_clear:
                clear.append(p)
        return clear

    def _get_spawn_points(self):
        points = []
        for row_index, row in enumerate(self.map_data):
            for col_index, tile_type in enumerate(row):
                if tile_type == 4:
                    x = col_index * TILESIZE + TILESIZE // 2
                    y = row_index * TILESIZE + TILESIZE // 2
                    points.append((x, y))
        return points

    def _group_by_side(self, points):
        groups = {'left': [], 'right': [], 'top': [], 'bottom': []}
        
        for p in points:
            dist_left = p[0]
            dist_right = WIDTH - p[0]
            dist_top = p[1]
            dist_bottom = HEIGHT - p[1]
            
            min_dist = min(dist_left, dist_right, dist_top, dist_bottom)
            
            if min_dist == dist_left:
                groups['left'].append(p)
            elif min_dist == dist_right:
                groups['right'].append(p)
            elif min_dist == dist_top:
                groups['top'].append(p)
            else:
                groups['bottom'].append(p)
                
        return groups

    def _spawn_standard_group(self, points):
        possible = [1, 2, 3, 4, 5, 6]
        weights = [2, 4, 4, 4, 3, 2]
        num = random.choices(possible, weights=weights, k=1)[0]
        num = max(2, num)

        chosen = random.sample(points, min(num, len(points)))
        for pos in chosen:
            Enemy(pos, [self.visible_sprites, self.enemy_sprites], self.player,
                  enemy_type=0, obstacle_sprites=self.obstacle_sprites)

    def _spawn_spikey(self, points):
        if points:
            pos = random.choice(points)
            Enemy(pos, [self.visible_sprites, self.enemy_sprites], self.player,
                  enemy_type=6, obstacle_sprites=self.obstacle_sprites)

    def shoot(self, direction):
        if not self.player or not self.player.alive or self.shoot_cooldown > 0:
            return
        offset = (direction[0] * 28, direction[1] * 28)
        spawn_pos = (self.player.rect.centerx + offset[0], self.player.rect.centery + offset[1])
        Bullet(spawn_pos, direction, [self.visible_sprites, self.bullet_sprites], self.obstacle_sprites)
        self.shoot_cooldown = self.shoot_rate

    def render(self, surface=None):
        if surface is None:
            return
        surface.fill('black')

        for sprite in self.visible_sprites:
            if not isinstance(sprite, (Player, Bullet, Enemy)):
                surface.blit(sprite.image, sprite.rect)

        self.bullet_sprites.draw(surface)
        self.enemy_sprites.draw(surface)

        if self.player:
            surface.blit(self.player.image, self.player.rect)