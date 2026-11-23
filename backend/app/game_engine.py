"""GameEngine: the run-level state machine.

Flow: combat -> (win) card reward -> combat ... -> after 3 wins, boss ->
(win) victory / (die) defeat.

Owns RunState and delegates combat rules to CombatService, pile mechanics
to DeckService, randomness to injected RNG. Framework-free and UI-free.
"""
import random

from .cards import STARTING_DECK, get_card
from .combat import CombatService
from .deck import DeckService
from .enemies import make_enemy
from .models import CombatState, Phase, PlayerState, RunState

NORMAL_ENCOUNTERS = ["slime", "goblin", "brute"]
BOSS_ID = "boss"
ENCOUNTERS_BEFORE_BOSS = 3
REWARD_POOL = ["strike", "defend", "heavy_strike", "quick_strike"]


class GameEngine:
    def __init__(self, seed: int,
                 combat_service: CombatService | None = None):
        self.rng = random.Random(seed)
        self.deck_service = DeckService(self.rng)
        self.combat_service = combat_service or CombatService(self.deck_service)
        self.state = RunState(seed=seed, phase=Phase.COMBAT)
        self.state.deck = [get_card(cid) for cid in STARTING_DECK]
        self._start_encounter()

    # ----- run flow ---------------------------------------------------------

    def _start_encounter(self) -> None:
        enemy_id = BOSS_ID if self.state.is_boss_fight else (
            NORMAL_ENCOUNTERS[self.state.encounters_won])
        self.state.combat = CombatState(
            player=PlayerState(),
            enemies=[make_enemy(enemy_id)],
            piles=self.deck_service.new_piles(self.state.deck),
        )
        self.combat_service.start_combat(self.state.combat)
        self._log(f"Encounter vs {self.state.combat.enemies[0].name} begins!")

    def _roll_rewards(self, count: int = 3) -> list:
        return [get_card(self.rng.choice(REWARD_POOL)) for _ in range(count)]

    def take_card_reward(self, card_id: str) -> None:
        """Pick one of the offered reward cards, then start the next fight."""
        if self.state.phase != Phase.CARD_REWARD:
            raise ValueError("No card reward is pending.")
        ids = [c.id for c in self.state.reward_options]
        if card_id not in ids:
            raise ValueError("Card is not one of the offered rewards.")
        self.state.deck.append(get_card(card_id))
        self._log(f"Added {get_card(card_id).name} to deck.")
        self._advance_after_reward()

    def skip_card_reward(self) -> None:
        if self.state.phase != Phase.CARD_REWARD:
            raise ValueError("No card reward is pending.")
        self._advance_after_reward()

    def _advance_after_reward(self) -> None:
        self.state.reward_options = []
        self.state.is_boss_fight = self.state.encounters_won >= ENCOUNTERS_BEFORE_BOSS
        self.state.phase = Phase.COMBAT
        self._start_encounter()

    # ----- combat passthrough (validates phase) ------------------------------

    def play_card(self, hand_index: int, target_index: int) -> list[str]:
        self._require_combat()
        line = self.combat_service.play_card(self.state.combat, hand_index,
                                             target_index)
        self._log(line)
        self._after_player_action()
        return [line]

    def end_turn(self) -> list[str]:
        self._require_combat()
        lines = self.combat_service.end_turn(self.state.combat)
        self._log(*lines)
        self._after_player_action()
        return lines

    def _after_player_action(self) -> None:
        combat = self.state.combat
        enemies_dead = all(not e.alive for e in combat.enemies)
        player_dead = not combat.player.alive
        if player_dead:
            self.state.phase = Phase.DEFEAT
            self._log("You were defeated. Run over.")
        elif enemies_dead:
            self.state.encounters_won += 1
            if self.state.is_boss_fight:
                self.state.phase = Phase.VICTORY
                self._log("The Warden falls. You win the run!")
            else:
                self.state.phase = Phase.CARD_REWARD
                self.state.reward_options = self._roll_rewards()
                self._log("Enemy defeated — choose a card reward.")

    def _require_combat(self) -> None:
        if self.state.phase != Phase.COMBAT:
            raise ValueError(f"Action not allowed in phase {self.state.phase.value}.")

    def _log(self, *lines: str) -> None:
        self.state.log.extend(lines)
        self.state.log = self.state.log[-50:]
