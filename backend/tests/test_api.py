"""API-layer tests using FastAPI TestClient (in-memory runs, no server)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def new_run():
    r = client.post("/api/runs")
    assert r.status_code == 200
    return r.json()


def test_create_run_returns_combat_state():
    run = new_run()
    assert run["phase"] == "combat"
    assert run["combat"]["player"]["hp"] == 50
    assert run["combat"]["player"]["energy"] == 3
    assert len(run["combat"]["piles"]["hand"]) == 5
    assert run["combat"]["piles"]["draw"] == 5
    assert run["combat"]["enemies"][0]["name"] == "Slime"
    assert run["combat"]["enemies"][0]["intent"]["kind"] == "attack"


def test_play_card_and_end_turn_roundtrip():
    run = new_run()
    rid = run["run_id"]
    r = client.post(f"/api/runs/{rid}/play", json={"hand_index": 0, "target_index": 0})
    assert r.status_code == 200
    data = r.json()
    assert data["combat"]["player"]["energy"] < 3
    assert len(data["combat"]["piles"]["hand"]) == 4

    r = client.post(f"/api/runs/{rid}/end-turn")
    assert r.status_code == 200
    data = r.json()
    assert data["combat"]["player"]["energy"] == 3
    assert len(data["combat"]["piles"]["hand"]) == 5


def test_invalid_action_returns_400():
    run = new_run()
    rid = run["run_id"]
    r = client.post(f"/api/runs/{rid}/play", json={"hand_index": 99})
    assert r.status_code == 400
    assert "index" in r.json()["detail"]


def test_unknown_run_returns_404():
    r = client.get("/api/runs/nope")
    assert r.status_code == 404


def fight_until_phase(rid, phase):
    for _ in range(200):
        state = client.get(f"/api/runs/{rid}").json()
        if state["phase"] != "combat" or state["phase"] == phase:
            break
        # Play any affordable card, then end turn.
        hand = state["combat"]["piles"]["hand"]
        energy = state["combat"]["player"]["energy"]
        for i, c in enumerate(hand):
            if c["energy_cost"] <= energy:
                client.post(f"/api/runs/{rid}/play",
                            json={"hand_index": i, "target_index": 0})
                break
        else:
            client.post(f"/api/runs/{rid}/end-turn")
            continue
        # after playing one card, loop re-checks; end turn when out of plays
        state = client.get(f"/api/runs/{rid}").json()
        if state["phase"] == "combat" and all(
                c["energy_cost"] > state["combat"]["player"]["energy"]
                for c in state["combat"]["piles"]["hand"]):
            client.post(f"/api/runs/{rid}/end-turn")
    return state


def test_reward_flow_via_api():
    run = new_run()
    rid = run["run_id"]
    state = fight_until_phase(rid, "card_reward")
    assert state["phase"] == "card_reward"
    options = state["reward"]["options"]
    assert len(options) == 3
    r = client.post(f"/api/runs/{rid}/reward", json={"card_id": options[0]["id"]})
    assert r.status_code == 200
    assert r.json()["phase"] == "combat"
    assert r.json()["deck_size"] == 11


def test_reward_skip():
    run = new_run()
    rid = run["run_id"]
    state = fight_until_phase(rid, "card_reward")
    assert state["phase"] == "card_reward"
    r = client.post(f"/api/runs/{rid}/reward", json={"card_id": None})
    assert r.status_code == 200
    assert r.json()["deck_size"] == 10
