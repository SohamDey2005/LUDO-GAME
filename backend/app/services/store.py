import json
import os
from typing import Dict
from app.models.game import GameState

# In-memory store for Phase 3 (will be replaced by DB later)
games_store: Dict[str, GameState] = {}
leaderboard_store: Dict[str, int] = {}
DB_FILE = "ludo_db.json"

def _load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                for k, v in data.get("games", {}).items():
                    games_store[k] = GameState(**v)
                leaderboard_store.update(data.get("leaderboard", {}))
        except Exception as e:
            print(f"Failed to load DB: {e}")

def _save_db():
    try:
        data = {
            "games": {k: v.model_dump(mode='json') for k, v in games_store.items()},
            "leaderboard": leaderboard_store
        }
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Failed to save DB: {e}")

_load_db()

def get_game(game_id: str) -> GameState:
    if game_id not in games_store:
        raise ValueError("Game not found")
    return games_store[game_id]

def save_game(game: GameState) -> None:
    games_store[game.id] = game
    _save_db()

def update_leaderboard(player_id: str, wins: int):
    leaderboard_store[player_id] = leaderboard_store.get(player_id, 0) + wins
    _save_db()

def get_leaderboard():
    # Sort by wins descending
    return sorted([{"player_id": k, "wins": v} for k, v in leaderboard_store.items()], key=lambda x: x["wins"], reverse=True)
