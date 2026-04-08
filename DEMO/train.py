import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
import os
import pandas as pd
import sys

from prairie_king.envs.prairie_king_env import PrairieKingEnv


class Logger(BaseCallback):
    def __init__(self, log_dir="./logs/", verbose=0):
        super().__init__(verbose)
        self.log_dir = log_dir
        self.episode_data = []
        self.episode_count = 0
        os.makedirs(log_dir, exist_ok=True)

    def _on_step(self) -> bool:
        if self.locals.get("dones") is not None and self.locals["dones"][0]:
            self.episode_count += 1
            info = self.locals["infos"][0]

            data = {
                "episode": self.episode_count,
                "timestep": self.num_timesteps,
                "total_reward": round(float(self.locals["rewards"][0]), 4),
                "episode_length": info.get("episode_length", 0),
                "level_reached": info.get("level", 1),
                "enemies_killed": info.get("enemies_killed", 0),
                "active_enemies": info.get("active_enemies", 0),
                "obtained_powerup": info.get("obtained_powerup", False),
            }
            self.episode_data.append(data)

            if self.episode_count % 25 == 0:
                self._save_data()

        return True

    def _save_data(self):
        df = pd.DataFrame(self.episode_data)
        df.to_csv(os.path.join(self.log_dir, "training_data.csv"), index=False)

        if len(df) > 0:
            grouped = df.groupby("level_reached").agg({
                "total_reward": ["mean", "max", "min"],
                "episode_length": ["mean", "max"],
                "enemies_killed": ["mean", "sum"],
                "active_enemies": "mean",
                "obtained_powerup": "mean"
            }).round(3)

            grouped.columns = ['avg_reward', 'max_reward', 'min_reward',
                              'avg_length', 'max_length',
                              'avg_kills', 'total_kills',
                              'avg_active_enemies', 'powerup_rate']
            
            grouped.to_csv(os.path.join(self.log_dir, "stats_by_level.csv"))
            print(f"   → Saved {self.episode_count} episodes | Level stats updated")

    def _on_training_end(self):
        self._save_data()
        print(f"\nAll training data saved to {self.log_dir}")


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
checkpoint_callback = CheckpointCallback(
    save_freq=50_000,
    save_path="./models/",
    name_prefix="balanced"
)

print("Training started (Balanced strategy)")
print("Press Ctrl+C at any time to gracefully stop and save everything.\n")

try:
    model.learn(
        total_timesteps=10_000_000,
        callback=[logger_callback, checkpoint_callback]
    )
except KeyboardInterrupt:
    print("\n\nTraining stopped by user (Ctrl+C)")
    logger_callback._on_training_end()
    model.save("prairie_king_balanced_interrupted")
    print("Model and all data saved successfully!")
    sys.exit(0)

model.save("prairie_king_balanced_final")
logger_callback._on_training_end()
print("\nTraining finished successfully!")