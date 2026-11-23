"""All game data models: plain dataclasses describing the game's things.

Models hold no game logic — a Card doesn't know how to deal damage.
"""
from dataclasses import dataclass, field
from enum import Enum


# ----- cards -------------------------------------------------------------

class CardType(str, Enum):
    ATTACK = "attack"
    SKILL = "skill"


@dataclass(frozen=True)
class Card:
    id: str          # template id, e.g. "strike" — many copies can exist in a deck
    name: str
    description: str
    type: CardType
    energy_cost: int


# ----- player & piles ----------------------------------------------------

@dataclass
class PlayerState:
    hp: int = 50
    max_hp: int = 50
    energy: int = 3
    max_energy: int = 3
    block: int = 0

    @property
    def alive(self) -> bool:
        return self.hp > 0


@dataclass
class DeckPiles:
    """The three card piles used during combat."""
    draw: list[Card] = field(default_factory=list)
    hand: list[Card] = field(default_factory=list)
    discard: list[Card] = field(default_factory=list)


# ----- combat ------------------------------------------------------------

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
    # Internal bookkeeping for behaviour (move cycle position).
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


# ----- run ---------------------------------------------------------------

class Phase(str, Enum):
    COMBAT = "combat"            # player must act in combat
    CARD_REWARD = "card_reward"  # player picks one of three cards
    VICTORY = "victory"          # boss defeated, run complete
    DEFEAT = "defeat"            # player died


@dataclass
class RunState:
    seed: int
    phase: Phase
    encounters_won: int = 0      # 3 normal encounters, then boss
    is_boss_fight: bool = False
    deck: list[Card] = field(default_factory=list)   # full deck outside combat
    combat: CombatState | None = None
    reward_options: list[Card] = field(default_factory=list)
    log: list[str] = field(default_factory=list)     # recent events, newest last
