# ⚔️ Mini Spire

A simplified, playable deck-building roguelike inspired by Slay the Spire.
Built as a software engineering learning project: clean layering, testable rules, and a small but complete gameplay loop.

## Gameplay

- Turn-based card combat: 3 energy per turn, draw 5 cards, block absorbs damage and resets each turn.
- 4 cards: Strike, Defend, Heavy Strike, Quick Strike — starting deck of 10.
- 3 normal enemies (Slime, Goblin, Brute) with predictable attack intents, then a boss (The Warden).
- After each win, pick 1 of 3 random card rewards (or skip).
- Win the boss fight to complete the run.

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.14, FastAPI, Pydantic |
| Frontend | Vue 3, Vite |
| Storage | In-memory (JSON data models) |
| Tests | pytest (26 tests) |

## Project structure

```
mini-spire/
├─ backend/
│  ├─ app/
│  │  ├─ main.py            # FastAPI entry point (wires router, CORS)
│  │  ├─ api/
│  │  │  ├─ routes.py       # endpoints: parse input → call engine → return state
│  │  │  ├─ schemas.py      # Pydantic wire format (what the client sees)
│  │  │  └─ serialize.py    # domain models → API output
│  │  ├─ models/            # plain data classes: Card, PlayerState, CombatState, RunState...
│  │  ├─ cards.py           # card registry + effects (data-driven)
│  │  ├─ deck.py            # DeckService: draw / shuffle / discard
│  │  ├─ combat.py          # CombatService: combat rules, enemy turns
│  │  ├─ enemies.py         # enemy templates + deterministic move cycles
│  │  ├─ rewards.py         # RewardService
│  │  └─ game_engine.py     # run state machine (combat → reward → boss → end)
│  └─ tests/                # unit + API tests
└─ frontend/
   ├─ src/
   │  ├─ App.vue            # phase router: combat / reward / end screens
   │  ├─ api.js             # fetch client
   │  └─ components/        # CardView, EnemyCard, PlayerBar, CombatView, ...
   └─ vite.config.js        # dev proxy: /api → :8000
```

### Architectural rules

- **The engine is framework-free.** `game_engine.py`, `combat.py`, `deck.py` never import FastAPI or Vue. Illegal actions raise `ValueError`; the API layer translates that to HTTP 400.
- **Data-driven cards.** Each card is a registry entry (data + effect function). Adding a card never touches the combat engine.
- **Backend is the source of truth.** Every action returns the full run state; the frontend is a pure view and can't cheat (the draw pile is sent as a count, not card contents).
- **Deterministic where possible.** RNG is injected (`GameEngine(seed=...)`), enemies cycle fixed move lists — everything is unit-testable.

## Running

**Backend:**
```bash
cd mini-spire/backend
.venv/bin/python -m uvicorn app.main:app --port 8000
```
- API: http://localhost:8000
- Interactive docs (try it in-browser): http://localhost:8000/docs

**Frontend (second terminal):**
```bash
cd mini-spire/frontend
npm install     # first time only
npm run dev     # → http://localhost:5173
```

**Tests:**
```bash
cd mini-spire/backend
.venv/bin/python -m pytest tests -q
```

## API

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/runs` | Start a new run |
| GET | `/api/runs/{id}` | Get current run state |
| POST | `/api/runs/{id}/play` | Play a card (`{hand_index, target_index}`) |
| POST | `/api/runs/{id}/end-turn` | End the player's turn |
| POST | `/api/runs/{id}/reward` | Pick a reward card (`{card_id}`) or skip (`{card_id: null}`) |

Errors: unknown run → 404, illegal action → 400 with a readable message.

## Testing the full loop (headless)

```bash
pytest backend/tests/test_api.py   # drives real fights through the API
```

## Known limitations (v1)

- Runs are lost on server restart (in-memory storage).
- One enemy per encounter; targeting UI auto-selects the first living enemy (backend supports multiple).
- No deck viewer screen; `played_this_turn` tracked but unused by rules.
- Frontend has no automated tests (backend only).

## Ideas for v2

- Run persistence (JSON files or SQLite), multiple enemies per fight, potions/relics, card upgrades, deck viewer, frontend test suite.
