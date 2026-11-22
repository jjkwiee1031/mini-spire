"""Serializers: domain models -> Pydantic output models.

Kept in one place so both routes and future features share one mapping.
"""
from ..models.game import Phase, RunState
from .schemas import (
    CombatOut, EnemyOut, IntentOut, PilesOut, PlayerOut, RewardOut, RunOut,
)


def to_run_out(run_id: str, state: RunState) -> RunOut:
    combat = None
    if state.combat is not None:
        combat = CombatOut(
            player=PlayerOut(
                hp=state.combat.player.hp,
                max_hp=state.combat.player.max_hp,
                energy=state.combat.player.energy,
                max_energy=state.combat.player.max_energy,
                block=state.combat.player.block,
            ),
            enemies=[
                EnemyOut(
                    id=e.id, name=e.name, hp=e.hp, max_hp=e.max_hp,
                    block=e.block,
                    intent=IntentOut(kind=e.intent.kind, value=e.intent.value)
                    if e.intent else None,
                )
                for e in state.combat.enemies
            ],
            piles=PilesOut(
                draw=len(state.combat.piles.draw),
                hand=[_card_out(c) for c in state.combat.piles.hand],
                discard=len(state.combat.piles.discard),
            ),
            turn=state.combat.turn,
        )
    reward = None
    if state.phase == Phase.CARD_REWARD:
        reward = RewardOut(options=[_card_out(c) for c in state.reward_options])
    return RunOut(
        run_id=run_id,
        phase=state.phase,
        encounters_won=state.encounters_won,
        is_boss_fight=state.is_boss_fight,
        deck_size=len(state.deck),
        combat=combat,
        reward=reward,
        log=state.log,
    )


def _card_out(card):
    from .schemas import CardOut
    return CardOut(
        id=card.id, name=card.name, description=card.description,
        type=card.type, energy_cost=card.energy_cost,
    )
