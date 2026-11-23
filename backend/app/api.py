"""API layer: one file for routes, wire schemas, and serialization.

Thin layer over the game engine: parse input -> call engine -> return state.
Illegal actions (engine ValueError) become HTTP 400; unknown runs become 404.
Runs live in an in-memory dict; restarting the server wipes them (v1).
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .game_engine import GameEngine
from .models import CardType, IntentKind, Phase, RunState

router = APIRouter()

# run_id -> engine
_runs: dict[str, GameEngine] = {}


# ----- request schemas ----------------------------------------------------

class PlayCardIn(BaseModel):
    hand_index: int
    target_index: int = 0


class RewardChoiceIn(BaseModel):
    card_id: str | None = None  # None = skip reward


# ----- output schemas (what the frontend is allowed to see) ---------------

class CardOut(BaseModel):
    id: str
    name: str
    description: str
    type: CardType
    energy_cost: int


class IntentOut(BaseModel):
    kind: IntentKind
    value: int


class EnemyOut(BaseModel):
    id: str
    name: str
    hp: int
    max_hp: int
    block: int
    intent: IntentOut | None


class PlayerOut(BaseModel):
    hp: int
    max_hp: int
    energy: int
    max_energy: int
    block: int


class PilesOut(BaseModel):
    draw: int  # counts only — frontend never sees pile order
    hand: list[CardOut]
    discard: int


class CombatOut(BaseModel):
    player: PlayerOut
    enemies: list[EnemyOut]
    piles: PilesOut
    turn: int


class RewardOut(BaseModel):
    options: list[CardOut]


class RunOut(BaseModel):
    run_id: str
    phase: Phase
    encounters_won: int
    is_boss_fight: bool
    deck_size: int
    combat: CombatOut | None
    reward: RewardOut | None
    log: list[str] = Field(default_factory=list)


# ----- domain -> wire format ----------------------------------------------

def _card_out(card) -> CardOut:
    return CardOut(
        id=card.id, name=card.name, description=card.description,
        type=card.type, energy_cost=card.energy_cost,
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


# ----- helpers -------------------------------------------------------------

def _engine(run_id: str) -> GameEngine:
    engine = _runs.get(run_id)
    if engine is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    return engine


def _run_action(fn, *args):
    """Call an engine action, translating ValueError into HTTP 400."""
    try:
        return fn(*args)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ----- routes ---------------------------------------------------------------

@router.post("/runs", response_model=RunOut)
def create_run() -> RunOut:
    import secrets
    import uuid
    run_id = uuid.uuid4().hex[:12]
    _runs[run_id] = GameEngine(seed=secrets.randbits(32))
    return to_run_out(run_id, _runs[run_id].state)


@router.get("/runs/{run_id}", response_model=RunOut)
def get_run(run_id: str) -> RunOut:
    return to_run_out(run_id, _engine(run_id).state)


@router.post("/runs/{run_id}/play", response_model=RunOut)
def play_card(run_id: str, body: PlayCardIn) -> RunOut:
    engine = _engine(run_id)
    _run_action(engine.play_card, body.hand_index, body.target_index)
    return to_run_out(run_id, engine.state)


@router.post("/runs/{run_id}/end-turn", response_model=RunOut)
def end_turn(run_id: str) -> RunOut:
    engine = _engine(run_id)
    _run_action(engine.end_turn)
    return to_run_out(run_id, engine.state)


@router.post("/runs/{run_id}/reward", response_model=RunOut)
def choose_reward(run_id: str, body: RewardChoiceIn) -> RunOut:
    engine = _engine(run_id)
    if body.card_id is None:
        _run_action(engine.skip_card_reward)
    else:
        _run_action(engine.take_card_reward, body.card_id)
    return to_run_out(run_id, engine.state)
