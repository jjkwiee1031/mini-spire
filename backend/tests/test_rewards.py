import random

from app.cards import STARTING_DECK, get_card
from app.game_engine import GameEngine


def test_starting_deck_has_10_cards():
    assert len(STARTING_DECK) == 10


def test_rewards_are_three_cards_from_pool():
    eng = GameEngine(seed=0)
    cards = eng._roll_rewards()
    assert len(cards) == 3
    for c in cards:
        assert c.id in ("strike", "defend", "heavy_strike", "quick_strike")


def test_get_card_returns_fresh_instances():
    a, b = get_card("strike"), get_card("strike")
    assert a == b and a is not b
