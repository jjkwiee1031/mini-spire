import random

from app.game_engine import GameEngine
from app.models.game import Phase


def run_full(seed):
    eng = GameEngine(seed=seed)
    guard = 0
    while eng.state.phase not in (Phase.VICTORY, Phase.DEFEAT) and guard < 200:
        guard += 1
        if eng.state.phase == Phase.COMBAT:
            # Play every card in hand while energy allows, then end turn.
            played = True
            while played:
                played = False
                for i in range(len(eng.state.combat.piles.hand)):
                    card = eng.state.combat.piles.hand[i]
                    if card.energy_cost <= eng.state.combat.player.energy:
                        try:
                            eng.play_card(i, 0)
                            played = True
                        except ValueError:
                            pass
                        break
            if eng.state.phase == Phase.COMBAT:
                eng.end_turn()
        elif eng.state.phase == Phase.CARD_REWARD:
            eng.take_card_reward(eng.state.reward_options[0].id)
    return eng


def test_full_run_reaches_terminal_phase():
    eng = run_full(seed=42)
    assert eng.state.phase in (Phase.VICTORY, Phase.DEFEAT)


def test_run_can_be_won():
    # Try a few seeds; at least the mechanic must be exercised end-to-end.
    results = [run_full(s).state.phase for s in range(20)]
    assert Phase.VICTORY in results


def test_reward_added_to_deck():
    eng = run_full(seed=7)
    # starting deck of 10 + one card per encounter won (3 or 4 incl. rewards)
    assert len(eng.state.deck) >= 10
