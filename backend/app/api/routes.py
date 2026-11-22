"""API routes. Thin layer: parse input, call engine, serialize output.

Runs live in an in-memory dict. Illegal actions (engine ValueError) become
HTTP 400; unknown runs become 404.
"""
from fastapi import APIRouter, HTTPException

from ..game_engine import GameEngine
from .schemas import PlayCardIn, RewardChoiceIn, RunOut
from .serialize import to_run_out

router = APIRouter()

# run_id -> engine. In-memory only; restarts wipe games (accepted for v1).
_runs: dict[str, GameEngine] = {}


def _engine(run_id: str) -> GameEngine:
    engine = _runs.get(run_id)
    if engine is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    return engine


def _bad_request(fn, *args) -> dict:
    try:
        fn(*args)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {}


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
    _bad_request(engine.play_card, body.hand_index, body.target_index)
    return to_run_out(run_id, engine.state)


@router.post("/runs/{run_id}/end-turn", response_model=RunOut)
def end_turn(run_id: str) -> RunOut:
    engine = _engine(run_id)
    _bad_request(engine.end_turn)
    return to_run_out(run_id, engine.state)


@router.post("/runs/{run_id}/reward", response_model=RunOut)
def choose_reward(run_id: str, body: RewardChoiceIn) -> RunOut:
    engine = _engine(run_id)
    if body.card_id is None:
        _bad_request(engine.skip_card_reward)
    else:
        _bad_request(engine.take_card_reward, body.card_id)
    return to_run_out(run_id, engine.state)
