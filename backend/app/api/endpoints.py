from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict
import uuid

from app.models.game import GameState, Color, PlayerType
from app.services.game_engine import GameEngine
from app.services.store import save_game, get_game
from app.sockets.manager import manager
from app.ai.engine import AIEngine

router = APIRouter()

class JoinRequest(BaseModel):
    name: str
    player_type: PlayerType

class MoveRequest(BaseModel):
    player_id: str
    token_id: str

@router.post("/create", response_model=GameState)
async def create_game():
    game = GameEngine.create_game()
    GameEngine.add_player(game, "Player 1", Color.RED, PlayerType.HUMAN)
    GameEngine.add_player(game, "Player 2", Color.GREEN, PlayerType.HUMAN)
    GameEngine.add_player(game, "Player 3", Color.YELLOW, PlayerType.HUMAN)
    GameEngine.add_player(game, "Player 4", Color.BLUE, PlayerType.HUMAN)
    GameEngine.start_game(game)
    save_game(game)
    return game

@router.post("/{game_id}/join", response_model=GameState)
async def join_game(game_id: str, request: JoinRequest):
    try:
        game = get_game(game_id)
        
        # Determine next available color
        available_colors = [c for c in [Color.RED, Color.GREEN, Color.YELLOW, Color.BLUE] if c not in game.players]
        if not available_colors:
            raise ValueError("Game room is full")
            
        color = available_colors[0]
        GameEngine.add_player(game, request.name, color, request.player_type)
        
        # Start game automatically if 4 players joined
        if len(game.players) == 4:
            GameEngine.start_game(game)
            
        save_game(game)
        await manager.broadcast_game_state(game_id, game.model_dump(mode='json'))
        return game
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{game_id}", response_model=GameState)
async def get_game_state(game_id: str):
    try:
        return get_game(game_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{game_id}/roll", response_model=GameState)
async def roll_dice(game_id: str):
    try:
        game = get_game(game_id)
        GameEngine.roll_dice(game)
        save_game(game)
        await manager.broadcast_game_state(game_id, game.model_dump(mode='json'))
        return game
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{game_id}/force-roll/{value}", response_model=GameState)
async def force_roll(game_id: str, value: int):
    """Debug endpoint to force a specific dice roll."""
    try:
        game = get_game(game_id)
        if game.dice_value is not None:
            raise ValueError("Dice already rolled")
            
        game.dice_value = value
        game.last_action = f"DEBUG: Forced roll {value} for {game.current_turn.value}."
        
        from app.core.rules import RulesEngine
        if value == 6:
            game.consecutive_sixes += 1
            if game.consecutive_sixes == 3:
                game.last_action += " Three consecutive sixes! penalty triggered."
                GameEngine.rollback_turn(game)
                GameEngine.next_turn(game)
        else:
            game.consecutive_sixes = 0
            
        valid_tokens = RulesEngine.get_valid_moves(game, game.current_turn, game.dice_value)
        if not valid_tokens:
            game.last_action += " No valid moves available."
            GameEngine.next_turn(game)
            
        save_game(game)
        await manager.broadcast_game_state(game_id, game.model_dump(mode='json'))
        return game
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{game_id}/move", response_model=GameState)
async def move_token(game_id: str, request: MoveRequest):
    try:
        game = get_game(game_id)
        
        # Check if already finished
        was_finished = game.status.value == "finished"
        
        GameEngine.move_token(game, request.token_id)
        
        # Check if just finished
        if not was_finished and game.status.value == "finished" and game.winner:
            winner_player = game.players[game.winner]
            from app.services.store import update_leaderboard
            update_leaderboard(winner_player.name, 1)
            
        save_game(game)
        await manager.broadcast_game_state(game_id, game.model_dump(mode='json'))
        return game
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{game_id}/ai-move", response_model=GameState)
async def ai_move(game_id: str):
    try:
        game = get_game(game_id)
        if game.dice_value is None:
            GameEngine.roll_dice(game)
            save_game(game)
            await manager.broadcast_game_state(game_id, game.model_dump(mode='json'))
            return game
            
        best_token_id = AIEngine.get_best_move(game, difficulty="hard")
        if best_token_id:
            GameEngine.move_token(game, best_token_id)
        else:
            GameEngine.next_turn(game)
            
        save_game(game)
        await manager.broadcast_game_state(game_id, game.model_dump(mode='json'))
        return game
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
