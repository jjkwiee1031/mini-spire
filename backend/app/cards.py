"""Card registry and card effects.

Effects are functions taking a CardEffectContext and doing exactly one thing.
The combat engine only looks cards up here — adding a new card never touches
the engine.
"""
from dataclasses import dataclass, replace

from .models.cards import Card, CardType


@dataclass
class CardEffectContext:
    """Everything an effect might need. Engine fills it in."""
    combat: "CombatState"          # noqa: F821 - defined in models.combat
    target_enemy_index: int


@dataclass(frozen=True)
class CardDefinition:
    card: Card
    effect: callable  # (ctx: CardEffectContext) -> str  (returns a log line)


def deal_damage(ctx: CardEffectContext, amount: int) -> str:
    enemy = ctx.combat.enemies[ctx.target_enemy_index]
    blocked = min(enemy.block, amount)
    enemy.block -= blocked
    enemy.hp -= amount - blocked
    if enemy.hp < 0:
        enemy.hp = 0
    return f"Dealt {amount} damage to {enemy.name} ({blocked} blocked)."


def gain_block(ctx: CardEffectContext, amount: int) -> str:
    ctx.combat.player.block += amount
    return f"Player gains {amount} Block."


STRIKE = CardDefinition(
    card=Card("strike", "Strike", "Deal 6 damage.", CardType.ATTACK, 1),
    effect=lambda ctx: deal_damage(ctx, 6),
)
DEFEND = CardDefinition(
    card=Card("defend", "Defend", "Gain 5 Block.", CardType.SKILL, 1),
    effect=lambda ctx: gain_block(ctx, 5),
)
HEAVY_STRIKE = CardDefinition(
    card=Card("heavy_strike", "Heavy Strike", "Deal 14 damage.", CardType.ATTACK, 2),
    effect=lambda ctx: deal_damage(ctx, 14),
)
QUICK_STRIKE = CardDefinition(
    card=Card("quick_strike", "Quick Strike", "Deal 3 damage.", CardType.ATTACK, 0),
    effect=lambda ctx: deal_damage(ctx, 3),
)

# All cards that can appear in decks and rewards.
CARD_REGISTRY: dict[str, CardDefinition] = {
    d.card.id: d
    for d in (STRIKE, DEFEND, HEAVY_STRIKE, QUICK_STRIKE)
}

# Starting deck: 5 Strikes, 4 Defends, 1 Quick Strike = 10 cards.
STARTING_DECK: list[str] = (
    ["strike"] * 5 + ["defend"] * 4 + ["quick_strike"]
)

# Reward pool weights — modest cards more common.
REWARD_POOL: list[str] = ["strike", "defend", "heavy_strike", "quick_strike"]


def get_card(card_id: str) -> Card:
    """Return a fresh Card instance for a template id."""
    return replace(CARD_REGISTRY[card_id].card)
