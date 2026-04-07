import gymnasium as gym
from gymnasium import spaces
import pygame
import numpy as np
from ..world import World
from ..constants import WIDTH, HEIGHT, FPS, TILESIZE
from .strategies import STRATEGIES

class PrairieKingEnv(gym.Env):
    metadata = {"render_modes": ["human", None], "render_fps": FPS}

    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode
        self.strategy = STRATEGIES["balanced"]

        if render_mode == "human":
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.clock = pygame.time.Clock()
            pygame.display.set_caption(f"Prairie King RL - {self.strategy.name}")
        else:
            self.screen = None
            self.clock = None

        self.world = World()
        
        self.prev_enemy_count = 0
        self.prev_level = 1

        self.action_space = spaces.MultiDiscrete([9, 9])
        
        self.observation_space = spaces.Box(low=-2.0, high=2.0, shape=(42,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.world.reset(level=1)
        self.prev_enemy_count = 0
        self.prev_level = 1
        
        if self.render_mode == "human":
            self.render()
        return self._get_obs(), {}

    def step(self, action):
        move_action, shoot_action = action
        current_enemy_count = len(self.world.enemy_sprites)

        self.world.step(move_action)

        if shoot_action != 0:
            shoot_index = shoot_action - 1
            shoot_dirs = [
                (0, -1), (0, 1), (-1, 0), (1, 0),
                (-1, -1), (1, -1), (-1, 1), (1, 1)
            ]
            self.world.shoot(shoot_dirs[shoot_index])

        obs = self._get_obs()
        terminated = not self.world.player.alive
        truncated = False
        
        reward = self._compute_reward(current_enemy_count)

        info = {
            "level": self.world.current_level,
            "enemies_killed": max(0, current_enemy_count - len(self.world.enemy_sprites)),
            "active_enemies": len(self.world.enemy_sprites)
        }

        if self.render_mode == "human":
            self.render()
            self.clock.tick(FPS)

        return obs, reward, terminated, truncated, info

    def _get_obs(self):
        obs = np.zeros(42, dtype=np.float32)
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
            base = 30 + i * 2
            obs[base] = (pu.rect.centerx - p.rect.centerx) / WIDTH
            pt_map = {"coffee": 0.2, "machinegun": 0.4, "shotgun": 0.6, "wheel": 0.8, "star": 1.0}
            obs[base+1] = pt_map.get(pu.power_type, 0.0)

        obs[36] = 1.0 if self.world.shoot_cooldown == 0 else 0.0
        obs[37] = self.world.machinegun_timer / 720.0
        obs[38] = self.world.shotgun_timer / 720.0
        obs[39] = self.world.wheel_timer / 720.0
        obs[40] = self.world.star_timer / 720.0
        obs[41] = min(len(self.world.enemy_sprites) / 30.0, 1.0)

        return obs

    def _is_obstacle_at(self, x, y):
        for obs in self.world.obstacle_sprites:
            if obs.rect.collidepoint(x, y):
                return True
        return False

    def _compute_reward(self, prev_enemy_count):
        reward = self.strategy.survival_reward

        if not self.world.player.alive:
            reward += self.strategy.death_penalty
            return reward

        current_enemy_count = len(self.world.enemy_sprites)
        if current_enemy_count < prev_enemy_count:
            reward += (prev_enemy_count - current_enemy_count) * self.strategy.kill_reward

        if self.world.current_level > self.prev_level:
            reward += self.strategy.level_bonus
            self.prev_level = self.world.current_level

        reward -= (current_enemy_count * 0.005)

        return reward

    def render(self):
        if self.render_mode == "human" and self.screen:
            self.world.render(self.screen)
            pygame.display.flip()

    def close(self):
        if self.render_mode == "human":
            pygame.quit()