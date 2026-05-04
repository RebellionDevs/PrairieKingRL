# 🤠 PrairieKingRL

A Reinforcement Learning agent trained to play **Journey of the Prairie King** — the retro top-down shooter mini-game from Stardew Valley — built from scratch with Pygame and trained using **PPO** via Stable Baselines3.

---

## 🎬 Demo

<!-- Replace the link below with your YouTube video URL -->
[![Watch the demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

> 📌 **How to use:** Replace `YOUR_VIDEO_ID` in both the image URL and the link with your actual YouTube video ID  
> (e.g. for `https://www.youtube.com/watch?v=dQw4w9WgXcQ` the ID is `dQw4w9WgXcQ`)

---

## 📖 Overview

PrairieKingRL is a custom Gymnasium environment that recreates Journey of the Prairie King as an RL training ground. The agent controls a cowboy who must survive waves of enemies across multiple levels, learning to move, shoot, and collect power-ups — all from a compact vector observation.

---

## ✨ Features

- **Custom Gymnasium environment** built with Pygame
- **PPO training** via Stable Baselines3 with 16 parallel environments
- **Entropy scheduling** — exploration decays smoothly over 100M timesteps
- **49-dimensional observation space** including:
  - Player position
  - 8-direction wall proximity sensors
  - Positions of the 10 nearest enemies
  - Positions and types of the 3 nearest power-ups
  - Weapon cooldowns, active power-up timers, and enemy density per screen quadrant
- **MultiDiscrete action space** — move (9 directions) × shoot (9 directions)
- **5 power-ups**: Coffee (speed), Machine Gun (rapid fire), Shotgun (spread), Wheel (all-direction fire), Star (combo boost)
- **3 cycling levels** with increasing enemy variety
- **Live debug overlay** while watching the agent (toggle with `V` / `I` keys)
- **Training logger** — saves episode stats to CSV and auto-saves best/latest model checkpoints

---

## 🏗️ Project Structure

```
DEMO/
├── train.py                        # Train the PPO agent
├── human.py                        # Watch the trained agent play
├── prairie_king/
│   ├── constants.py                # Screen size, FPS, tile size
│   ├── world.py                    # Game world: spawning, physics, power-ups
│   ├── maps.py                     # Level map definitions
│   ├── entities/
│   │   ├── player.py
│   │   ├── enemy.py
│   │   ├── bullet.py
│   │   ├── powerup.py
│   │   └── tile.py
│   └── envs/
│       ├── prairie_king_env.py     # Gymnasium environment
│       └── strategies.py          # Reward strategy definitions
└── utils/
    └── graphics.py
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- [Pygame](https://www.pygame.org/)
- [Gymnasium](https://gymnasium.farama.org/)
- [Stable Baselines3](https://stable-baselines3.readthedocs.io/)
- pandas, numpy

Install dependencies:

```bash
pip install pygame gymnasium stable-baselines3 pandas numpy
```

### Train the Agent

```bash
cd DEMO
python train.py
```

Training runs for **100 million timesteps** across 16 parallel environments. Checkpoints are saved every 500k steps to `models/` and episode stats are logged to `logs/training_data.csv`.  
Stop at any time with `Ctrl+C` — progress is saved automatically.

### Watch the Trained Agent Play

```bash
cd DEMO
python human.py
```

This loads the saved model and renders the agent playing in real time.  
**Controls while watching:**
| Key | Action |
|-----|--------|
| `V` | Toggle debug vectors (enemy/powerup lines + wall sensors) |
| `I` | Toggle the info overlay panel |
| `ESC` / close window | Exit |

---

## 🎮 Environment Details

| Property | Value |
|----------|-------|
| Observation space | `Box(-2, 2, shape=(49,), float32)` |
| Action space | `MultiDiscrete([9, 9])` — move + shoot |
| Reward on kill | `+10` |
| Level clear bonus | `+50` |
| Power-up pickup | `+20` |
| Death penalty | `-400` |
| Survival reward | `+0.00015` per tick |
| FPS | 60 |
| Arena size | 1024 × 1024 px (16 × 16 tiles) |

---

## 📊 Training Logs

Each saved CSV row contains:

| Column | Description |
|--------|-------------|
| `episode` | Episode number |
| `timestep` | Global step at episode end |
| `total_reward` | Cumulative episode reward |
| `episode_length` | Ticks survived |
| `level_reached` | Highest level reached |
| `enemies_killed` | Total enemies killed |
| `shots_fired` | Total shots fired |
| `powerups_collected` | Total power-ups collected |
| `distance_km` | Approximate distance traveled |

---

## 🛠️ Hyperparameters

| Parameter | Value |
|-----------|-------|
| Algorithm | PPO |
| Policy | MlpPolicy `[256, 256]` |
| Learning rate | `3e-4` |
| n_steps | `4096` |
| Batch size | `1024` |
| Epochs | `10` |
| Gamma | `0.999` |
| Entropy coef | `0.1` → `0.005` (scheduled) |
| Parallel envs | `16` |
| Total timesteps | `100,000,000` |

---

## 📝 License

This project is for educational and research purposes. Prairie King is originally a mini-game from [Stardew Valley](https://www.stardewvalley.net/) by ConcernedApe.
