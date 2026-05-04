# PrairieKingRL
A Reinforcement Learning agent trained to play **Journey of the Prairie King** — the retro top-down shooter mini-game from Stardew Valley — built from scratch with Pygame and trained using **PPO** via Stable Baselines3.

The primary goal of this project is to develop an AI agent capable of earning the rarest achievement in Stardew Valley: completing "Journey of the Prairie King" without a single death (Fector's Challenge).
---
## Demo
[![Watch the demo](https://img.youtube.com/vi/9fN6DUlRqzY/maxresdefault.jpg)](https://www.youtube.com/watch?v=9fN6DUlRqzY)
---
## Overview
PrairieKingRL is a custom Gymnasium environment that recreates Journey of the Prairie King as an RL training ground. The agent controls a cowboy who must survive waves of enemies across multiple levels, learning to move, shoot, and collect power-ups — all from a compact vector observation.
---
## Features
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
- **Live debug overlay** while watching the agent (toggle with `V` / `I` keys)
- **Training logger** — saves episode stats to CSV and auto-saves best/latest model checkpoints
---
## Getting Started
### Prerequisites
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
__________________________________________________________________
| Key | Action                                                    |
|-----|-----------------------------------------------------------|
| `V` | Toggle debug vectors (enemy/powerup lines + wall sensors) |
| `I` | Toggle the info overlay panel                             |
| `ESC` / close window | Exit                                     |
|_________________________________________________________________|
---
## 📝 License
This project is for educational and research purposes. Prairie King is originally a mini-game from [Stardew Valley](https://www.stardewvalley.net/) by ConcernedApe.
