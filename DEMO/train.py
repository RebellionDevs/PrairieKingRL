import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import BaseCallback, CallbackList
import os
import pandas as pd
import sys
import numpy as np

from prairie_king.envs.prairie_king_env import PrairieKingEnv

class EntropyScheduleCallback(BaseCallback):
    def __init__(self, start_ent, end_ent, total_steps, verbose=0):
        super(EntropyScheduleCallback, self).__init__(verbose)
        self.start_ent = start_ent
        self.end_ent = end_ent
        self.total_steps = total_steps

    def _on_step(self) -> bool:
        progress = min(self.num_timesteps / self.total_steps, 1.0)
        current_ent = self.start_ent + progress * (self.end_ent - self.start_ent)
        self.model.ent_coef = current_ent
        self.logger.record("train/ent_coef_manual", current_ent)
        return True

class Logger(BaseCallback):
    def __init__(self, log_dir="./logs/", save_path="./models/", verbose=0):
        super().__init__(verbose)
        self.log_dir = log_dir
        self.save_path = save_path
        self.episode_data = []
        self.episode_count = 0
        self.best_mean_reward = -np.inf
        self.save_freq = 500_000
        self.last_time_save = 0
        self.pixels_to_km = 32 * 1000
        
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.num_timesteps - self.last_time_save >= self.save_freq:
            self.last_time_save = self.num_timesteps
            path = os.path.join(self.save_path, "balanced_latest.zip")
            self.model.save(path)
            if self.verbose > 0:
                print(f"Saved latest model checkpoint to {path}")

        if self.locals.get("dones") is not None:
            for env_idx, done in enumerate(self.locals["dones"]):
                if done:
                    self.episode_count += 1
                    info = self.locals["infos"][env_idx]
                    ep_info = info.get("episode")

                    dist_px = info.get("distance_traveled", 0.0)
                    dist_km = dist_px / self.pixels_to_km

                    data = {
                        "episode": self.episode_count,
                        "timestep": self.num_timesteps,
                        "total_reward": round(float(ep_info['r'] if ep_info else self.locals["rewards"][env_idx]), 4),
                        "episode_length": info.get("ticks_survived", 0),
                        "level_reached": info.get("level", 1),
                        "enemies_killed": info.get("enemies_killed", 0),
                        "shots_fired": info.get("shots_fired", 0),
                        "powerups_collected": info.get("powerups_collected", 0),
                        "distance_km": round(dist_km, 4)
                    }
                    self.episode_data.append(data)

                    self.logger.record("env/enemies_killed", data["enemies_killed"])
                    self.logger.record("env/shots_fired", data["shots_fired"])
                    self.logger.record("env/distance_km", data["distance_km"])

            if self.episode_count % 100 == 0 and self.episode_data:
                self._save_data()
                recent_rewards = [d["total_reward"] for d in self.episode_data[-50:]]
                current_mean = np.mean(recent_rewards)
                if current_mean > self.best_mean_reward:
                    self.best_mean_reward = current_mean
                    self.model.save(os.path.join(self.save_path, "balanced_best.zip"))

        return True

    def _save_data(self):
        df = pd.DataFrame(self.episode_data)
        df.to_csv(os.path.join(self.log_dir, "training_data.csv"), index=False)

    def _on_training_end(self):
        self._save_data()

def make_env():
    return PrairieKingEnv(render_mode=None)

total_training_steps = 100_000_000
vec_env = make_vec_env(make_env, n_envs=12)
model_path = "prairie_king_balanced_final.zip"

if os.path.exists(model_path):
    print(f"Resuming training from: {model_path}")
    model = PPO.load(model_path, env=vec_env, verbose=1)
else:
    print("Starting fresh training...")
    model = PPO(
        "MlpPolicy",
        vec_env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=4096,
        batch_size=512,
        n_epochs=10,
        gamma=0.999,
        ent_coef=0.1,
        policy_kwargs=dict(net_arch=[256, 256]),
        tensorboard_log="./logs/PrairieKing_Balanced/",
        device="auto"
    )

entropy_callback = EntropyScheduleCallback(
    start_ent=0.1,
    end_ent=0.005,
    total_steps=total_training_steps
)
logger_callback = Logger(log_dir="./logs/", save_path="./models/", verbose=1)
callbacks = CallbackList([entropy_callback, logger_callback])

print("\nTraining started. Press Ctrl+C to stop.\n")

try:
    model.learn(
        total_timesteps=total_training_steps,
        callback=callbacks,
        reset_num_timesteps=False
    )
except KeyboardInterrupt:
    print("\nTraining stopped. Saving...")
    model.save("prairie_king_balanced_final")
    sys.exit(0)

model.save("prairie_king_balanced_final")
print("\nDone!")