import gymnasium as gym
from gymnasium import spaces
import pygame
import numpy as np
import math
from ..world import World
from ..constants import WIDTH, HEIGHT, FPS, TILESIZE
from .strategies import STRATEGIES

class PrairieKingEnv(gym.Env):
    metadata = {"render_modes": ["human", None], "render_fps": FPS}

    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode
        self.strategy = STRATEGIES["balanced"]

        self.show_debug_vectors = False
        self.show_info_panel = True
        self.last_reward = 0.0
        self.episode_reward = 0.0

        if render_mode == "human":
            pygame.init()
            pygame.font.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont("Consolas", 13)
            pygame.display.set_caption(f"Prairie King RL - {self.strategy.name}")
        else:
            self.screen = None
            self.clock = None
            self.font = None

        self.world = World(render_mode=render_mode)
        
        self.prev_enemy_count = 0
        self.prev_level = 1
        self.ticks_survived = 0
        self.current_shoot_action = 0
        
        self.total_enemies_killed = 0
        self.total_shots_fired = 0
        self.total_powerups_collected = 0
        self.total_distance_pixels = 0.0
        self.prev_player_pos = (0, 0)

        self.action_space = spaces.MultiDiscrete([9, 9])
        self.observation_space = spaces.Box(low=-2.0, high=2.0, shape=(49,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.world.reset(level=1)
        self.prev_enemy_count = 0
        self.prev_level = 1
        self.ticks_survived = 0
        self.current_shoot_action = 0
        self.last_reward = 0.0
        self.episode_reward = 0.0
        
        self.total_enemies_killed = 0
        self.total_shots_fired = 0
        self.total_powerups_collected = 0
        self.total_distance_pixels = 0.0
        self.prev_player_pos = self.world.player.rect.center
        
        if self.render_mode == "human":
            self.render()
        return self._get_obs(), {}

    def step(self, action):
        move_action, shoot_action = action
        self.current_shoot_action = shoot_action
        current_enemy_count = len(self.world.enemy_sprites)

        self.world.step(move_action)
        self.ticks_survived += 1
        
        curr_pos = self.world.player.rect.center
        dist = math.sqrt((curr_pos[0] - self.prev_player_pos[0])**2 + (curr_pos[1] - self.prev_player_pos[1])**2)
        self.total_distance_pixels += dist
        self.prev_player_pos = curr_pos

        if shoot_action != 0:
            if self.world.shoot_cooldown == 0:
                self.total_shots_fired += 1
                
                shoot_index = shoot_action - 1
                shoot_dirs = [
                    (0, -1), (0, 1), (-1, 0), (1, 0),
                    (-1, -1), (1, -1), (-1, 1), (1, 1)
                ]
                self.world.shoot(shoot_dirs[shoot_index])

        obs = self._get_obs()
        terminated = not self.world.player.alive
        truncated = False

        killed_this_step = max(0, current_enemy_count - len(self.world.enemy_sprites))
        self.total_enemies_killed += killed_this_step
        
        if self.world.last_step_pickup:
            self.total_powerups_collected += 1

        self.last_reward = self._compute_reward(current_enemy_count)
        self.episode_reward += self.last_reward

        info = {
            "level": self.world.current_level,
            "enemies_killed": self.total_enemies_killed,
            "active_enemies": len(self.world.enemy_sprites),
            "obtained_powerup": self.world.last_step_pickup,
            "ticks_survived": self.ticks_survived,
            "shots_fired": self.total_shots_fired,
            "powerups_collected": self.total_powerups_collected,
            "distance_traveled": self.total_distance_pixels,
            "episode_reward": self.episode_reward
        }

        if self.render_mode == "human":
            self.render()
            self.clock.tick(FPS)

        return obs, self.last_reward, terminated, truncated, info

    def _get_obs(self):
        obs = np.zeros(49, dtype=np.float32)
        p = self.world.player
        if not p or not p.alive:
            return obs

        obs[0] = p.rect.centerx / WIDTH
        obs[1] = p.rect.centery / HEIGHT

        scan_directions = [(0,-1), (0,1), (-1,0), (1,0), (-1,-1), (1,-1), (-1,1), (1,1)]
        for i, d in enumerate(scan_directions):
            for step in range(1, 4):
                test_x = p.rect.centerx + d[0] * step * TILESIZE
                test_y = p.rect.centery + d[1] * step * TILESIZE
                if self._is_obstacle_at(test_x, test_y):
                    obs[2+i] = 1.0 / step
                    break

        enemies = sorted(self.world.enemy_sprites, 
                         key=lambda e: (e.rect.centerx - p.rect.centerx)**2 + (e.rect.centery - p.rect.centery)**2)[:10]
        for i, enemy in enumerate(enemies):
            base = 10 + i * 2
            obs[base] = (enemy.rect.centerx - p.rect.centerx) / WIDTH
            obs[base+1] = (enemy.rect.centery - p.rect.centery) / HEIGHT

        powerups = sorted(self.world.powerup_sprites, 
                          key=lambda pu: (pu.rect.centerx - p.rect.centerx)**2 + (pu.rect.centery - p.rect.centery)**2)[:3]
        for i, pu in enumerate(powerups):
            base = 30 + i * 3
            obs[base] = (pu.rect.centerx - p.rect.centerx) / WIDTH
            obs[base+1] = (pu.rect.centery - p.rect.centery) / HEIGHT
            pt_map = {"coffee": 0.2, "machinegun": 0.4, "shotgun": 0.6, "wheel": 0.8, "star": 1.0}
            obs[base+2] = pt_map.get(pu.power_type, 0.0)

        obs[39] = 1.0 if self.world.shoot_cooldown == 0 else 0.0
        obs[40] = self.world.machinegun_timer / 720.0
        obs[41] = self.world.shotgun_timer / 720.0
        obs[42] = self.world.wheel_timer / 720.0
        obs[43] = self.world.star_timer / 720.0
        obs[44] = min(len(self.world.enemy_sprites) / 30.0, 1.0)

        quads = [0, 0, 0, 0]
        total_e = len(self.world.enemy_sprites)
        if total_e > 0:
            for enemy in self.world.enemy_sprites:
                ex, ey = enemy.rect.centerx, enemy.rect.centery
                if ey < HEIGHT / 2:
                    if ex < WIDTH / 2: quads[0] += 1
                    else: quads[1] += 1
                else:
                    if ex < WIDTH / 2: quads[2] += 1
                    else: quads[3] += 1
            obs[45] = quads[0] / total_e
            obs[46] = quads[1] / total_e
            obs[47] = quads[2] / total_e
            obs[48] = quads[3] / total_e

        return obs

    def _is_obstacle_at(self, x, y):
        for obstacle in self.world.obstacle_sprites:
            if obstacle.rect.collidepoint(x, y):
                return True
        return False

    def _compute_reward(self, prev_enemy_count):
        reward = 0
        if self.world.wave_timer < self.world.wave_duration:
            reward = self.strategy.survival_reward
        else:
            overtime = self.world.wave_timer - self.world.wave_duration
            reward -= 0.005 * overtime 

        if not self.world.player.alive:
            return self.strategy.death_penalty
            
        current_enemy_count = len(self.world.enemy_sprites)

        if current_enemy_count < prev_enemy_count:
            killed = prev_enemy_count - current_enemy_count
            reward += killed * self.strategy.kill_reward

        if self.world.current_level != self.prev_level:
            reward += self.strategy.level_bonus
            self.prev_level = self.world.current_level

        if self.world.last_step_pickup:
            reward += self.strategy.powerup_pickup_bonus

        if self.current_shoot_action != 0:
            if self.world.shoot_cooldown == 0:
                reward -= 5
            else:
                reward -= 0.001

        reward -= (current_enemy_count * 0.01)
        return reward

    def render(self):
        if self.render_mode != "human" or not self.screen:
            return

        for event in pygame.event.get(pygame.KEYDOWN):
            if event.key == pygame.K_v:
                self.show_debug_vectors = not self.show_debug_vectors
            if event.key == pygame.K_i:
                self.show_info_panel = not self.show_info_panel

        self.world.render(self.screen, show_vectors=self.show_debug_vectors)

        if self.show_info_panel:
            overlay = pygame.Surface((280, 200), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (5, 5))

            obs = self._get_obs()
            enemies = self.world.enemy_sprites
            p_pos = self.world.player.rect.center
            
            danger_level = 0.0
            if enemies:
                min_dist = min([np.linalg.norm(np.array(p_pos) - np.array(e.rect.center)) for e in enemies])
                danger_level = max(0.0, 1.0 - (min_dist / 250.0))

            shoot_dirs = ["NONE", "UP", "DOWN", "LEFT", "RIGHT", "UL", "UR", "DL", "DR"]
            
            lines = [
                f"TOTAL REWARD: {self.episode_reward:.2f}",
                f"STEP REWARD: {self.last_reward:.4f}",
                f"DANGER LVL: {danger_level:.1%}",
                f"WALL SENSOR: {'NEAR' if any(obs[2:10] > 0) else 'CLEAR'}",
                f"ACTION SHOOT: {shoot_dirs[self.current_shoot_action]}",
                f"ENEMIES ACT: {len(enemies)}",
                f"--------------------",
                f"[V] VECTORS | [I] PANEL"
            ]

            for i, text in enumerate(lines):
                color = (255, 255, 255)
                if "TOTAL REWARD" in text:
                    color = (255, 215, 0)
                elif "STEP REWARD" in text:
                    color = (50, 255, 50) if self.last_reward > 0 else (255, 50, 50)
                
                txt_surf = self.font.render(text, True, color)
                self.screen.blit(txt_surf, (15, 15 + i * 20))

            center_r = (230, 150)
            pygame.draw.circle(self.screen, (70, 70, 70), center_r, 25, 1)
            if self.current_shoot_action != 0:
                dirs = [(0,0), (0,-1), (0,1), (-1,0), (1,0), (-1,-1), (1,-1), (-1,1), (1,1)]
                vec = dirs[self.current_shoot_action]
                end_p = (center_r[0] + vec[0]*22, center_r[1] + vec[1]*22)
                pygame.draw.line(self.screen, (0, 255, 255), center_r, end_p, 3)

        pygame.display.flip()

    def close(self):
        if self.render_mode == "human":
            pygame.quit()