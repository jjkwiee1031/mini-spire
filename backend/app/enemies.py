"""Enemy definitions and behaviour.

Enemies cycle through a fixed, ordered move list (deterministic and
predictable for the player and tests). A move is an Intent; `_move_index`
in EnemyState is how far into the cycle the enemy is.
"""
from .models import EnemyState, Intent, IntentKind

# (kind, value) per move, cycled in order.
ENEMY_TEMPLATES: dict[str, dict] = {
    "slime": {
        "name": "Slime",
        "hp": 20,
        "moves": [
            (IntentKind.ATTACK, 5),
            (IntentKind.BLOCK, 3),
        ],
    },
    "goblin": {
        "name": "Goblin",
        "hp": 30,
        "moves": [
            (IntentKind.ATTACK, 7),
            (IntentKind.ATTACK, 4),
            (IntentKind.BLOCK, 4),
        ],
    },
    "brute": {
        "name": "Brute",
        "hp": 45,
        "moves": [
            (IntentKind.ATTACK, 10),
            (IntentKind.ATTACK, 6),
        ],
    },
    "boss": {
        "name": "The Warden",
        "hp": 80,
        "moves": [
            (IntentKind.ATTACK, 12),
            (IntentKind.BLOCK, 8),
            (IntentKind.ATTACK, 8),
        ],
    },
}


def make_enemy(enemy_id: str) -> EnemyState:
    template = ENEMY_TEMPLATES[enemy_id]
    return EnemyState(
        id=enemy_id,
        name=template["name"],
        hp=template["hp"],
        max_hp=template["hp"],
    )


def next_intent(enemy_id: str, move_index: int) -> Intent:
    """The intent for the enemy's upcoming move (1-based move_index)."""
    moves = ENEMY_TEMPLATES[enemy_id]["moves"]
    kind, value = moves[(move_index - 1) % len(moves)]
    return Intent(kind=kind, value=value)
