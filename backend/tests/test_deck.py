from app.deck import DeckService
from app.models.cards import Card, CardType
from app.models.deck import DeckPiles


def make_card(i: int) -> Card:
    return Card(f"c{i}", f"Card {i}", "", CardType.ATTACK, 1)


def make_deck(n: int) -> list[Card]:
    return [make_card(i) for i in range(n)]


def test_draw_moves_cards_to_hand():
    svc = DeckService(rng=__import__("random").Random(0))
    piles = svc.new_piles(make_deck(10))
    svc.draw(piles, 5)
    assert len(piles.hand) == 5
    assert len(piles.draw) == 5
    assert len(piles.discard) == 0


def test_draw_from_discard_when_draw_empty():
    svc = DeckService(rng=__import__("random").Random(1))
    piles = DeckPiles(draw=make_deck(5), hand=[], discard=make_deck(10))
    svc.draw(piles, 5)
    assert len(piles.hand) == 5 and len(piles.draw) == 0
    # draw again: discard reshuffles into draw pile
    svc.draw(piles, 5)
    assert len(piles.hand) == 10 and len(piles.discard) == 0
    assert len(piles.draw) == 5  # leftovers stay in the draw pile


def test_draw_stops_when_deck_exhausted():
    svc = DeckService(rng=__import__("random").Random(2))
    piles = svc.new_piles(make_deck(3))
    drawn = svc.draw(piles, 5)
    assert len(drawn) == 3 and len(piles.hand) == 3


def test_discard_hand():
    svc = DeckService(rng=__import__("random").Random(3))
    piles = svc.new_piles(make_deck(4))
    svc.draw(piles, 4)
    svc.discard_hand(piles)
    assert piles.hand == [] and len(piles.discard) == 4
