"""Run-level state: where the player is in the run, and what happened."""
from dataclasses import dataclass, field
from enum import Enum

from .cards import Card
from .combat import CombatState


class Phase(str, Enum):
    COMBAT = "combat"          # player must act in combat
    CARD_REWARD = "card_reward"  # player picks one of three cards
    VICTORY = "victory"        # boss defeated, run complete
    DEFEAT = "defeat"          # player died


@dataclass
class RunState:
    seed: int
    phase: Phase
    encounters_won: int = 0          # 3 normal encounters, then boss
    is_boss_fight: bool = False
    deck: list[Card] = field(default_factory=list)   # full deck outside combat
    combat: CombatState | None = None
    reward_options: list[Card] = field(default_factory=list)
    log: list[str] = field(default_factory=list)     # recent events, newest last
