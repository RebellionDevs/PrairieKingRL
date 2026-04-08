import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
import os
import pandas as pd

from prairie_king.envs.prairie_king_env import PrairieKingEnv

class Logger(BaseCallback):
    def __init__(self, log_dir = './logs/', verbose = 0):
        super().__init__(verbose)
        self.log_dir = log_dir
        self.episode_data = []
        self.ecount = 0
        os.makedirs(log_dir, exist_ok=True)

    def _on_step(self):
        if self.locals.get("dones") is not None and self.locals["dones"][0]:
            self.ecount += 1
            info = self.locals["infos"][0]

            data = {
                "episode": self.ecount,
                "timestep": self.num_timesteps,
                "total_reward": round(float(self.locals["rewards"][0]), 4),
                "episode_length": info.get("episode_length", 0),
                "level_reached": info.get("level", 1),
                "enemies_killed": info.get("enemies_killed", 0),
                "active_enemies_at_end": info.get("active_enemies", 0),
                "obtained_powerup": info.get("obtained_powerup", False),
            }
            self.episode_data.append(data)

            if self.ecount % 25 == 0:
                df = pd.DataFrame(self.episode_data)
                df.to_csv(os.path.join(self.log_dir, "training_data.csv"), index=False)

        return True
    
    def _on_training_end(self):
        df = pd.DataFrame(self.episode_data)
        df.to_csv(os.path.join(self.log_dir, "training_data.csv"), index=False)

def make_env():
    return PrairieKingEnv(render_mode=None)

vec_env = make_vec_env(make_env, n_envs=8)

model = PPO(
    "MlpPolicy",
    vec_env,
    verbose=1,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=512,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    ent_coef=0.01,
    tensorboard_log="./logs/PrairieKing_Balanced/",
    device="auto"
)

logger_callback = Logger(log_dir="./logs/")

checkpoint_callback = CheckpointCallback(save_freq=50_000, save_path="./models/", name_prefix="balanced")

model.learn(
    total_timesteps=3_000_000,
    callback=[logger_callback, checkpoint_callback]
)

model.save("prairie_king_balanced_final")