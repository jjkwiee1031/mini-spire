"""RewardService: random card rewards after each encounter."""
import random

from .cards import REWARD_POOL, get_card


class RewardService:
    def __init__(self, rng: random.Random):
        self.rng = rng

    def roll_rewards(self, count: int = 3) -> list:
        return [get_card(self.rng.choice(REWARD_POOL)) for _ in range(count)]
