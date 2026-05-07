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
async def roll_dice(game_id: str, background_tasks: BackgroundTasks):
    try:
        game = get_game(game_id)
        roll = GameEngine.roll_dice(game)
        
        # Check if no valid moves or if 3-sixes penalty triggered
        valid_tokens = RulesEngine.get_valid_moves(game, game.current_turn, game.dice_value) if game.dice_value else []
        is_penalty = game.consecutive_sixes == 3
        
        save_game(game)
        await manager.broadcast_game_state(game_id, game.model_dump(mode='json'))
        
        if not valid_tokens or is_penalty:
            # Handle delayed skip
            import asyncio
            async def delayed_skip():
                await asyncio.sleep(1.5)
                # Re-fetch in case state changed
                g = get_game(game_id)
                GameEngine.next_turn(g)
                save_game(g)
                await manager.broadcast_game_state(game_id, g.model_dump(mode='json'))
            
            background_tasks.add_task(delayed_skip)
            
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
async def ai_move(game_id: str, background_tasks: BackgroundTasks):
    try:
        game = get_game(game_id)
        if game.dice_value is None:
            # Re-use the roll logic with delay
            return await roll_dice(game_id, background_tasks)
            
        best_token_id = AIEngine.get_best_move(game, difficulty="hard")
        if best_token_id:
            GameEngine.move_token(game, best_token_id)
        else:
            # No moves, should have been handled by roll_dice delay, 
            # but safety fallback here
            GameEngine.next_turn(game)
            
        save_game(game)
        await manager.broadcast_game_state(game_id, game.model_dump(mode='json'))
        return game
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
