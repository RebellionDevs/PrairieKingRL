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
    def __init__(self, render_mode=None):
        self.render_mode = render_mode
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.powerup_sprites = pygame.sprite.Group()

        self.player = None
        self.last_step_pickup = False
        self.current_level = 1
        self.spawn_queue = []

        self.shoot_cooldown = 0
        self.shoot_rate = 22

        self.wave_timer = 0
        self.wave_duration = 5500
        self.spawn_timer = 0

        self.coffee_timer = 0
        self.machinegun_timer = 0
        self.shotgun_timer = 0
        self.wheel_timer = 0
        self.star_timer = 0

    def reset(self, level):
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        self.powerup_sprites.empty()
        self.spawn_queue = []

        self.current_level = level
        self.shoot_cooldown = 0
        self.shoot_rate = 22
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
                    tile_groups = [self.visible_sprites] if self.render_mode == "human" else []
                    tile = Tile((x, y), tile_groups, tile_type, render_mode=self.render_mode)
                    if tile_type in (1, 6):
                        self.obstacle_sprites.add(tile)

        center_x = (WIDTH // 2) - (TILESIZE // 2)
        center_y = (HEIGHT // 2) - (TILESIZE // 2)
        player_groups = [self.visible_sprites] if self.render_mode == "human" else []
        self.player = Player((center_x, center_y), player_groups, self.obstacle_sprites, render_mode=self.render_mode)

    def step(self, move_action: int):
        if not self.player or not self.player.alive:
            return
        
        self.last_step_pickup = False

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
                enemy_groups = [self.visible_sprites, self.enemy_sprites] if self.render_mode == "human" else [self.enemy_sprites]
                Enemy(item['pos'], enemy_groups, self.player,
                      enemy_type=item['type'], obstacle_sprites=self.obstacle_sprites,
                      on_death=self._maybe_drop_powerup, render_mode=self.render_mode)
                self.spawn_queue.remove(item)
            else:
                item['delay'] -= 1

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self.wave_timer += 1
        if self.spawn_timer > 0:
            self.spawn_timer -= 1

        if self.spawn_timer <= 0 and self.wave_timer < self.wave_duration:
            self.spawn_wave()
            self.spawn_timer = 600

        hits = pygame.sprite.groupcollide(self.bullet_sprites, self.enemy_sprites, True, False)
        for bullet, enemies in hits.items():
            if enemies:
                enemies[0].take_damage(1)

        if pygame.sprite.spritecollideany(self.player, self.enemy_sprites):
            self.player.take_damage()

        if self._check_powerup_pickup():
            self.last_step_pickup = True

        if self.wave_timer >= self.wave_duration and len(self.enemy_sprites) == 0:
            self.reset(((self.current_level) % 3) + 1)

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
        if not self.player: return False
        picked = pygame.sprite.spritecollide(self.player, self.powerup_sprites, True)
        if picked:
            for p in picked: 
                self._apply_powerup(p.power_type)
            return True
        return False

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
        if random.random() < 0.10:
            self._drop_powerup(pos)

    def _drop_powerup(self, pos):
        power_types = ["coffee", "machinegun", "shotgun", "wheel", "star"]
        powerup_groups = [self.visible_sprites, self.powerup_sprites] if self.render_mode == "human" else [self.powerup_sprites]
        PowerUp(pos, powerup_groups, random.choice(power_types), render_mode=self.render_mode)

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
            bullet_groups = [self.visible_sprites, self.bullet_sprites] if self.render_mode == "human" else [self.bullet_sprites]
            Bullet(spawn_pos, (d.x, d.y), bullet_groups, self.obstacle_sprites, render_mode=self.render_mode)

    def render(self, surface=None, show_vectors=False):
        if surface is None: 
            return
            
        surface.fill('black')
        
        for sprite in self.visible_sprites:
            if not isinstance(sprite, (Player, Bullet, Enemy)):
                surface.blit(sprite.image, sprite.rect)
                
        self.bullet_sprites.draw(surface)
        self.enemy_sprites.draw(surface)
        self.powerup_sprites.draw(surface)
        
        if self.player:
            surface.blit(self.player.image, self.player.rect)
            
            if show_vectors:
                p_pos = self.player.rect.center
                
                for enemy in self.enemy_sprites:
                    pygame.draw.line(surface, (255, 50, 50), p_pos, enemy.rect.center, 1)
                    
                for pu in self.powerup_sprites:
                    pygame.draw.line(surface, (50, 255, 50), p_pos, pu.rect.center, 2)
                

                scan_directions = [
                    (0,-1), (0,1), (-1,0), (1,0), 
                    (-1,-1), (1,-1), (-1,1), (1,1)
                ]
                for d in scan_directions:
                    end_pos = (
                        p_pos[0] + d[0] * TILESIZE * 3,
                        p_pos[1] + d[1] * TILESIZE * 3
                    )
                    pygame.draw.line(surface, (255, 255, 0), p_pos, end_pos, 1)