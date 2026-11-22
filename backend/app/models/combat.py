"""Combat-related models: enemy runtime state and player-visible intents."""
from dataclasses import dataclass, field
from enum import Enum

from .cards import Card
from .deck import DeckPiles
from .player import PlayerState


class IntentKind(str, Enum):
    ATTACK = "attack"
    BLOCK = "block"


@dataclass(frozen=True)
class Intent:
    kind: IntentKind
    value: int  # damage the attack will deal, or block it will gain


@dataclass
class EnemyState:
    id: str
    name: str
    hp: int
    max_hp: int
    block: int = 0
    intent: Intent | None = None
    # Internal bookkeeping for behaviour (e.g. move cycle position).
    _move_index: int = 0

    @property
    def alive(self) -> bool:
        return self.hp > 0


@dataclass
class CombatState:
    player: PlayerState
    enemies: list[EnemyState]
    piles: DeckPiles
    turn: int = 1
    # Cards played this turn, in order (for UI highlighting / log).
    played_this_turn: list[Card] = field(default_factory=list)
