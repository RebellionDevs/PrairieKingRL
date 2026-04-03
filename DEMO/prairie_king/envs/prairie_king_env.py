import gymnasium as gym
from gymnasium import spaces
import pygame
import numpy as np
from ..world import World
from ..constants import WIDTH, HEIGHT, FPS

class PrairieKingEnv(gym.Env):
    metadata = {"render_modes": ["human", None], "render_fps": FPS}

    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode
        self.world = World()

        # Action: 0=noop, 1=up, 2=down, 3=left, 4=right
        self.action_space = spaces.Discrete(5)

        # Simple vector obs for now (player x/y normalized). Fast for training.
        # You can change to pixel obs later (see comment below).
        self.observation_space = spaces.Box(low=0, high=1, shape=(2,), dtype=np.float32)

        # Human mode only: real window
        self.screen = None
        self.clock = None
        if render_mode == "human":
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.clock = pygame.time.Clock()

    def reset(self, seed=None, options=None):
        self.world.reset(level=1)
        if self.render_mode == "human":
            self.render()
        return self._get_obs(), {}

    def step(self, action):
        self.world.step(action)
        obs = self._get_obs()
        reward = 0.01  # tiny survival reward (you can change later)
        terminated = False
        truncated = False  # you can add max steps later
        info = {}

        if self.render_mode == "human":
            self.render()
            self.clock.tick(FPS)

        return obs, reward, terminated, truncated, info

    def _get_obs(self):
        # Vector obs based on current ready code only
        px = self.world.player.rect.centerx / WIDTH
        py = self.world.player.rect.centery / HEIGHT
        return np.array([px, py], dtype=np.float32)

    def render(self):
        if self.render_mode == "human" and self.screen:
            self.world.render(self.screen)
            pygame.display.flip()

    def close(self):
        if self.render_mode == "human":
            pygame.quit()