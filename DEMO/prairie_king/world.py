import pygame
import random
from .maps import get_map
from .constants import TILESIZE, WIDTH, HEIGHT
from .entities.tile import Tile
from .entities.player import Player
from .entities.bullet import Bullet
from .entities.enemy import Enemy
from .entities.powerup import PowerUp

class World:
    def __init__(self):
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.powerup_sprites = pygame.sprite.Group()

        self.player = None
        self.current_level = 1
        self.spawn_queue = []

        self.shoot_cooldown = 0
        self.shoot_rate = 22

        self.wave_timer = 0
        self.wave_duration = 5400
        self.spawn_timer = 0

        self.coffee_timer = 0
        self.machinegun_timer = 0
        self.shotgun_timer = 0
        self.wheel_timer = 0
        self.star_timer = 0

        self.reset(level=1)

    def reset(self, level):
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        self.powerup_sprites.empty()
        self.spawn_queue = []

        self.current_level = level
        self.shoot_cooldown = 0
        self.wave_timer = 0
        self.spawn_timer = 180

        self.coffee_timer = 0
        self.machinegun_timer = 0
        self.shotgun_timer = 0
        self.wheel_timer = 0
        self.star_timer = 0

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

        dirs = {0:(0,0),1:(0,-1),2:(0,1),3:(-1,0),4:(1,0),
                5:(-1,-1),6:(1,-1),7:(-1,1),8:(1,1)}
        dx, dy = dirs.get(move_action, (0, 0))
        self.player.set_direction(dx, dy)
        self.player.update()

        self.bullet_sprites.update()
        self.enemy_sprites.update()
        self.powerup_sprites.update()

        for item in self.spawn_queue[:]:
            if item['delay'] <= 0:
                Enemy(item['pos'], [self.visible_sprites, self.enemy_sprites], self.player,
                      enemy_type=item['type'], obstacle_sprites=self.obstacle_sprites,
                      on_death=self._maybe_drop_powerup)
                self.spawn_queue.remove(item)
            else:
                item['delay'] -= 1

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

        self._check_powerup_pickup()

        if self.wave_timer >= self.wave_duration and len(self.enemy_sprites) == 0:
            self.reset(level=self.current_level + 1)

        if self.coffee_timer > 0:
            self.coffee_timer -= 1
            if self.coffee_timer == 0: self.player.speed = 5
        if self.machinegun_timer > 0:
            self.machinegun_timer -= 1
            if self.machinegun_timer == 0: self.shoot_rate = 22
        if self.shotgun_timer > 0: self.shotgun_timer -= 1
        if self.wheel_timer > 0: self.wheel_timer -= 1
        if self.star_timer > 0:
            self.star_timer -= 1
            if self.star_timer == 0:
                self.player.speed = 5
                self.shoot_rate = 22

    def _check_powerup_pickup(self):
        if not self.player: return
        picked = pygame.sprite.spritecollide(self.player, self.powerup_sprites, True)
        for p in picked: self._apply_powerup(p.power_type)

    def _apply_powerup(self, power_type):
        if power_type == "coffee":
            self.player.speed = 7.5
            self.coffee_timer = 960
        elif power_type == "machinegun":
            self.shoot_rate = 8
            self.machinegun_timer = 720
        elif power_type == "shotgun":
            self.shotgun_timer = 720
        elif power_type == "wheel":
            self.wheel_timer = 720
        elif power_type == "star":
            self.player.speed = 7.0
            self.shoot_rate = 10
            self.star_timer = 720

    def spawn_wave(self):
        spawn_points = self._get_spawn_points()
        if not spawn_points: return
        groups = self._group_by_side(spawn_points)

        for side, points in groups.items():
            if not points: continue
            
            is_spikey = (self.current_level > 1 and random.random() < 0.15)
            
            if is_spikey:
                pos = random.choice(points)
                self.spawn_queue.append({'pos': pos, 'type': 6, 'delay': 0})
            else:
                possible = [1, 2, 3, 4, 5, 6]
                weights = [1, 3, 4, 4, 3, 2]
                num = random.choices(possible, weights=weights, k=1)[0]
                
                for i in range(num):
                    delay = (i // len(points)) * 45 
                    pos = points[i % len(points)]
                    self.spawn_queue.append({'pos': pos, 'type': 0, 'delay': delay})

    def _get_spawn_points(self):
        points = []
        for r, row in enumerate(self.map_data):
            for c, tile in enumerate(row):
                if tile == 4:
                    points.append((c * TILESIZE + TILESIZE // 2, r * TILESIZE + TILESIZE // 2))
        return points

    def _group_by_side(self, points):
        groups = {'left': [], 'right': [], 'top': [], 'bottom': []}
        for p in points:
            d_l, d_r = p[0], WIDTH - p[0]
            d_t, d_b = p[1], HEIGHT - p[1]
            m = min(d_l, d_r, d_t, d_b)
            if m == d_l: groups['left'].append(p)
            elif m == d_r: groups['right'].append(p)
            elif m == d_t: groups['top'].append(p)
            else: groups['bottom'].append(p)
        return groups

    def _maybe_drop_powerup(self, pos):
        if random.random() < 0.07:
            self._drop_powerup(pos)

    def _drop_powerup(self, pos):
        power_types = ["coffee", "machinegun", "shotgun", "wheel", "star"]
        PowerUp(pos, [self.visible_sprites, self.powerup_sprites], random.choice(power_types))

    def shoot(self, direction):
        if not self.player or not self.player.alive or self.shoot_cooldown > 0:
            return

        current_rate = self.shoot_rate 

        if self.wheel_timer > 0:
            current_rate = min(current_rate, 12) 
        
        if self.shotgun_timer > 0:
            current_rate += 10

        self.shoot_cooldown = current_rate

        base_vec = pygame.math.Vector2(direction)
        if base_vec.magnitude() == 0:
            base_vec = pygame.math.Vector2(0, -1)
        else:
            base_vec = base_vec.normalize()

        final_directions = [base_vec]

        if self.wheel_timer > 0:
            final_directions = [
                pygame.math.Vector2(0, -1), pygame.math.Vector2(0, 1),
                pygame.math.Vector2(-1, 0), pygame.math.Vector2(1, 0),
                pygame.math.Vector2(-1, -1).normalize(), pygame.math.Vector2(1, -1).normalize(),
                pygame.math.Vector2(-1, 1).normalize(), pygame.math.Vector2(1, 1).normalize()
            ]

        if self.shotgun_timer > 0 or self.star_timer > 0:
            combined_dirs = []
            for d in final_directions:
                combined_dirs.append(d)
                combined_dirs.append(d.rotate(25))
                combined_dirs.append(d.rotate(-25))
            final_directions = combined_dirs

        spawn_pos = (
            self.player.rect.centerx + base_vec.x * 32,
            self.player.rect.centery + base_vec.y * 32
        )

        for d in final_directions:
            Bullet(spawn_pos, (d.x, d.y), [self.visible_sprites, self.bullet_sprites], self.obstacle_sprites)

    def render(self, surface=None):
        if surface is None: return
        surface.fill('black')
        for sprite in self.visible_sprites:
            if not isinstance(sprite, (Player, Bullet, Enemy)): surface.blit(sprite.image, sprite.rect)
        self.bullet_sprites.draw(surface)
        self.enemy_sprites.draw(surface)
        self.powerup_sprites.draw(surface)
        if self.player: surface.blit(self.player.image, self.player.rect)