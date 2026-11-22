"""Card data model.

A Card is pure data. What a card *does* is defined separately in
app/cards.py (the effect registry), keeping the engine data-driven.
"""
from dataclasses import dataclass
from enum import Enum


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
