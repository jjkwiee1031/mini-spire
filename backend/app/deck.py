"""DeckService: drawing, shuffling, discarding.

Owns nothing but pile manipulation — combat rules live in combat.py.
Takes an RNG callable so tests can force deterministic draws.
"""
import random as _random

from .models import Card, DeckPiles

class DeckService:
    def __init__(self, rng: _random.Random):
        self.rng = rng

    def new_piles(self, deck: list[Card]) -> DeckPiles:
        piles = DeckPiles(draw=list(deck), hand=[], discard=[])
        self.shuffle(piles)
        return piles

    def shuffle(self, piles: DeckPiles) -> None:
        self.rng.shuffle(piles.draw)

    def draw(self, piles: DeckPiles, count: int) -> list[Card]:
        drawn: list[Card] = []
        for _ in range(count):
            if not piles.draw:
                if not piles.discard:
                    break  # entire deck is in hand
                piles.draw = piles.discard
                piles.discard = []
                self.shuffle(piles)
            drawn.append(piles.draw.pop())
        piles.hand.extend(drawn)
        return drawn

    def discard_hand(self, piles: DeckPiles) -> None:
        piles.discard.extend(piles.hand)
        piles.hand.clear()

    def discard_from_hand(self, piles: DeckPiles, hand_index: int) -> Card:
        card = piles.hand.pop(hand_index)
        piles.discard.append(card)
        return card
