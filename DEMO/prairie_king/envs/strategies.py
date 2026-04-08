from dataclasses import dataclass

@dataclass
class RewardStrategy:
    name: str
    survival_reward: float = 0.0
    kill_reward: float = 0.0
    death_penalty: float = 0.0
    level_bonus: float = 0.0
    accuracy_bonus: float = 0.0
    miss_penalty: float = 0.0
    powerup_pickup_bonus: float = 0.0

STRATEGIES = {
    "balanced" : RewardStrategy(
        name="Balanced",
        survival_reward=0.015,
        kill_reward=5.0,
        death_penalty=-100.0,
        level_bonus=100.0,
        powerup_pickup_bonus=10.0,
    )
}