"""Pydantic schemas: what the API sends to the frontend.

These mirror the domain models but exist separately so the wire format can
evolve independently of the engine.
"""
from pydantic import BaseModel, Field

from ..models.cards import CardType
from ..models.combat import IntentKind
from ..models.game import Phase


class CardOut(BaseModel):
    id: str
    name: str
    description: str
    type: CardType
    energy_cost: int


class IntentOut(BaseModel):
    kind: IntentKind
    value: int


class EnemyOut(BaseModel):
    id: str
    name: str
    hp: int
    max_hp: int
    block: int
    intent: IntentOut | None


class PlayerOut(BaseModel):
    hp: int
    max_hp: int
    energy: int
    max_energy: int
    block: int


class PilesOut(BaseModel):
    draw: int  # counts only — frontend never sees pile order
    hand: list[CardOut]
    discard: int


class CombatOut(BaseModel):
    player: PlayerOut
    enemies: list[EnemyOut]
    piles: PilesOut
    turn: int


class RewardOut(BaseModel):
    options: list[CardOut]


class RunOut(BaseModel):
    run_id: str
    phase: Phase
    encounters_won: int
    is_boss_fight: bool
    deck_size: int
    combat: CombatOut | None
    reward: RewardOut | None
    log: list[str] = Field(default_factory=list)


class PlayCardIn(BaseModel):
    hand_index: int
    target_index: int = 0


class RewardChoiceIn(BaseModel):
    card_id: str | None = None  # None = skip reward
