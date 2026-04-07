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

STRATEGIES = {
    "balanced" : RewardStrategy(
        name="Balanced",
        survival_reward=0.008,
        kill_reward=10.0,
        death_penalty=-80.0,
        level_bonus=40.0,
    )
}