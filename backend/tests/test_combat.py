import random

from app.cards import CARD_REGISTRY
from app.combat import CombatService
from app.deck import DeckService
from app.enemies import make_enemy
from app.models import Card, CardType, CombatState, DeckPiles, PlayerState


def build_combat(deck_cards, enemy_id="slime", rng_seed=0):
    rng = random.Random(rng_seed)
    svc = CombatService(DeckService(rng))
    player = PlayerState()
    piles = DeckPiles(draw=list(deck_cards), hand=[], discard=[])
    combat = CombatState(player=player, enemies=[make_enemy(enemy_id)], piles=piles)
    # Deterministic opening "hand": put first 5 cards in hand directly.
    svc.deck.draw(combat.piles, 5)
    svc._set_intent(combat.enemies[0])  # initial intent (normally via start_combat)
    return svc, combat


def strike(n=1):
    return [Card("strike", "Strike", "", CardType.ATTACK, 1)] * n


def defend():
    return [Card("defend", "Defend", "", CardType.SKILL, 1)]


def test_attack_deals_damage_and_discards_card():
    svc, combat = build_combat(strike(5))
    combat.player.energy = 1
    log = svc.play_card(combat, 0, 0)
    assert "6 damage" in log
    assert combat.enemies[0].hp == 14  # 20 - 6
    assert combat.player.energy == 0
    assert len(combat.piles.hand) == 4
    assert len(combat.piles.discard) == 1


def test_attack_blocked_by_enemy_block():
    svc, combat = build_combat(strike(5))
    combat.player.energy = 1
    combat.enemies[0].block = 4
    svc.play_card(combat, 0, 0)
    assert combat.enemies[0].hp == 18  # 4 blocked
    assert combat.enemies[0].block == 0


def test_not_enough_energy_rejected():
    svc, combat = build_combat(strike(5))
    combat.player.energy = 0
    try:
        svc.play_card(combat, 0, 0)
        assert False, "should raise"
    except ValueError as e:
        assert "energy" in str(e)


def test_invalid_hand_index_rejected():
    svc, combat = build_combat(strike(5))
    try:
        svc.play_card(combat, 99, 0)
        assert False, "should raise"
    except ValueError:
        pass


def test_defend_gains_block():
    svc, combat = build_combat(strike(4) + defend())  # defend ends up last → drawn
    combat.player.energy = 1
    idx = next(i for i, c in enumerate(combat.piles.hand) if c.id == "defend")
    log = svc.play_card(combat, idx, 0)
    assert combat.player.block == 5


def test_end_turn_enemy_attacks_block_absorbs_then_resets():
    svc, combat = build_combat(strike(5))
    combat.player.energy = 3
    svc.play_card(combat, 0, 0)  # unused energy left
    svc.play_card(combat, 0, 0)  # discard another, whatever
    combat.player.block = 10
    hp_before = combat.player.hp
    log = svc.end_turn(combat)
    # Slime's first move: attack 5. Block 10 absorbs it fully.
    assert "attacks for 5" in log[0]
    assert combat.player.hp == hp_before
    # Block was consumed by the hit, then reset at start of next turn.
    assert combat.player.block == 0
    assert combat.turn == 2
    assert combat.player.block == 0
    assert combat.player.energy == 3
    assert len(combat.piles.hand) == 5


def test_enemy_intent_cycles_predictably():
    svc, combat = build_combat(strike(5), enemy_id="goblin")
    intents = []
    for _ in range(5):
        intents.append(combat.enemies[0].intent)
        svc.end_turn(combat)
    values = [i.value if i.kind.name == "ATTACK" else -i.value for i in intents]
    # goblin cycle: 7, 4, block, 7, 4
    assert values == [7, 4, -4, 7, 4]


def test_player_death_sets_hp_floor():
    svc, combat = build_combat(strike(5), enemy_id="brute")
    combat.player.hp = 3
    combat.player.block = 0
    svc.end_turn(combat)
    assert combat.player.hp == 0
    assert not combat.player.alive


def test_enemy_dies_at_zero_hp():
    svc, combat = build_combat(strike(5))
    combat.enemies[0].hp = 5
    combat.player.energy = 1
    svc.play_card(combat, 0, 0)
    assert combat.enemies[0].hp == 0
    assert not combat.enemies[0].alive


def test_quick_strike_costs_zero():
    card = CARD_REGISTRY["quick_strike"].card
    assert card.energy_cost == 0
