"""The three card piles used during combat."""
from dataclasses import dataclass, field

from .cards import Card


@dataclass
class DeckPiles:
    draw: list[Card] = field(default_factory=list)
    hand: list[Card] = field(default_factory=list)
    discard: list[Card] = field(default_factory=list)
