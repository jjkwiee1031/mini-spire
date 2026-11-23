"""CombatService: the rules of a single combat encounter.

Validates and executes player actions (play card, end turn) and enemy turns.
Raises ValueError with a readable message for illegal actions — the API layer
maps that to HTTP 400. No FastAPI imports here; the engine stays framework-free.
"""
from .cards import CARD_REGISTRY, CardEffectContext
from .models import CardType
from .deck import DeckService
from .models import CombatState, EnemyState, Intent, IntentKind

DRAW_PER_TURN = 5


class CombatService:
    def __init__(self, deck_service: DeckService):
        self.deck = deck_service

    # ----- player actions -------------------------------------------------

    def start_combat(self, combat: CombatState) -> None:
        """Draw the opening hand and set the first enemy intents."""
        self.deck.draw(combat.piles, DRAW_PER_TURN)
        for enemy in combat.enemies:
            self._set_intent(enemy)

    def play_card(self, combat: CombatState, hand_index: int,
                  target_index: int) -> str:
        if hand_index < 0 or hand_index >= len(combat.piles.hand):
            raise ValueError("Invalid card index.")
        card = combat.piles.hand[hand_index]

        definition = CARD_REGISTRY[card.id]
        if combat.player.energy < card.energy_cost:
            raise ValueError("Not enough energy.")

        # target_index is an index into the *living* enemies (what the UI
        # shows). Skills ignore it.
        if card.type == CardType.ATTACK:
            living = [e for e in combat.enemies if e.alive]
            if target_index < 0 or target_index >= len(living):
                raise ValueError("Attack cards need a valid living target.")
            target = combat.enemies.index(living[target_index])
        else:
            target = 0

        combat.player.energy -= card.energy_cost
        self.deck.discard_from_hand(combat.piles, hand_index)
        combat.played_this_turn.append(card)
        return definition.effect(CardEffectContext(combat, target))

    def end_turn(self, combat: CombatState) -> list[str]:
        """Discard hand, enemies act, then start the player's next turn.

        Returns log lines for what the enemies did.
        """
        log: list[str] = []
        self.deck.discard_hand(combat.piles)

        for enemy in combat.enemies:
            if enemy.alive and combat.player.alive:
                log.append(self._enemy_act(combat, enemy))

        if not combat.player.alive:
            return log

        # Start of player's next turn.
        combat.turn += 1
        combat.player.block = 0
        combat.player.energy = combat.player.max_energy
        combat.played_this_turn.clear()
        self.deck.draw(combat.piles, DRAW_PER_TURN)
        return log

    # ----- enemies ---------------------------------------------------------

    def _enemy_act(self, combat: CombatState, enemy: EnemyState) -> str:
        """Execute the enemy's current intent, then pick the next one."""
        intent = enemy.intent
        assert intent is not None
        if intent.kind == IntentKind.ATTACK:
            damage = intent.value
            blocked = min(combat.player.block, damage)
            combat.player.block -= blocked
            combat.player.hp -= damage - blocked
            line = f"{enemy.name} attacks for {damage} ({blocked} blocked)."
        else:
            enemy.block += intent.value
            line = f"{enemy.name} gains {intent.value} Block."
        if combat.player.hp < 0:
            combat.player.hp = 0
        self._set_intent(enemy)
        return line

    def _set_intent(self, enemy: EnemyState) -> None:
        """Predictable behaviour: enemies cycle through a fixed move list."""
        enemy._move_index += 1
        from .enemies import next_intent  # local import avoids circular deps
        enemy.intent = next_intent(enemy.id, enemy._move_index)
