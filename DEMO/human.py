import pygame
from stable_baselines3 import PPO
from prairie_king.envs.prairie_king_env import PrairieKingEnv

def run():
    env = PrairieKingEnv(render_mode="human")
    
    try:
        model = PPO.load("prairie_king_balanced_final")
        print("✅ Loaded model: prairie_king_balanced_final")
    except:
        try:
            model = PPO.load("models/best/best_model")
        except:
            return

    obs, _ = env.reset()
    episode = 0
    total_reward = 0

    print("\nWatching trained agent play...")
    print("Press ESC or close window to exit\n")

    while True:
        action, _ = model.predict(obs, deterministic=True)

        obs, reward, terminated, truncated, info = env.step(action)
        
        total_reward += reward

        if terminated:
            episode += 1
            print(f"Episode {episode} finished | Total Reward: {total_reward:.1f} | Level reached: {info.get('level', 1)}")
            total_reward = 0
            obs, _ = env.reset()

    env.close()


if __name__ == "__main__":
    run()