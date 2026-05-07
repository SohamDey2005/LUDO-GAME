from typing import Optional, Dict
import uuid
import json

from app.models.game import GameState, GameStatus, Color, Player, PlayerType, Token, TokenStatus
from app.core.dice import Dice
from app.core.rules import RulesEngine

class GameEngine:
    @staticmethod
    def create_game() -> GameState:
        """Initializes a new empty game state."""
        return GameState(
            id=str(uuid.uuid4()),
            players={},
            status=GameStatus.WAITING
        )

    @staticmethod
    def add_player(game_state: GameState, name: str, color: Color, player_type: PlayerType) -> Player:
        """Adds a player to the game."""
        if game_state.status != GameStatus.WAITING:
            raise ValueError("Game is already in progress")
        if color in game_state.players:
            raise ValueError(f"Color {color.value} is already taken")
        if len(game_state.players) >= 4:
            raise ValueError("Game is full")

        tokens = [Token(id=f"{color.value}_{i}", color=color) for i in range(4)]
        player = Player(id=str(uuid.uuid4()), name=name, color=color, player_type=player_type, tokens=tokens)
        game_state.players[color] = player
        return player

    @staticmethod
    def start_game(game_state: GameState) -> None:
        """Starts the game, setting the first turn."""
        if len(game_state.players) < 2:
            raise ValueError("Not enough players to start")
        
        game_state.status = GameStatus.IN_PROGRESS
        
        # Find the first available color in turn order
        for color in game_state.turn_order:
            if color in game_state.players:
                game_state.current_turn = color
                break
        
        # Take initial snapshot
        GameEngine.take_turn_snapshot(game_state)

    @staticmethod
    def take_turn_snapshot(game_state: GameState) -> None:
        """Takes a snapshot of the current player states to allow rollback."""
        # We only need to store the players and their token positions
        snapshot = {
            "players": {color.value: player.dict() for color, player in game_state.players.items()}
        }
        game_state.turn_snapshot = snapshot

    @staticmethod
    def rollback_turn(game_state: GameState) -> None:
        """Restores the game state from the turn snapshot."""
        if not game_state.turn_snapshot:
            return
            
        snapshot = game_state.turn_snapshot
        # Restore players
        for color_val, player_data in snapshot["players"].items():
            color = Color(color_val)
            game_state.players[color] = Player.parse_obj(player_data)
            
        game_state.last_action += " TURN ROLLED BACK TO START."

    @staticmethod
    def roll_dice(game_state: GameState) -> int:
        """Rolls the dice for the current player."""
        if game_state.status != GameStatus.IN_PROGRESS:
            raise ValueError("Game is not in progress")
        if game_state.dice_value is not None:
            raise ValueError("Dice already rolled for this turn")

        roll = Dice.roll()
        game_state.dice_value = roll
        game_state.last_action = f"Player {game_state.current_turn.value} rolled a {roll}."

        if roll == 6:
            game_state.consecutive_sixes += 1
            if game_state.consecutive_sixes == 3:
                # Rule 6: 3 consecutive sixes = forfeit turn AND rollback
                game_state.last_action += " Three consecutive sixes! penalty triggered."
                GameEngine.rollback_turn(game_state)
                GameEngine.next_turn(game_state)
                return roll
        else:
            game_state.consecutive_sixes = 0

        # Check if any valid moves exist
        valid_tokens = RulesEngine.get_valid_moves(game_state, game_state.current_turn, game_state.dice_value)
        game_state.movable_tokens = [t.id for t in valid_tokens]
        
        if not valid_tokens:
            game_state.last_action += " No valid moves available."
            GameEngine.next_turn(game_state)

        return roll

    @staticmethod
    def move_token(game_state: GameState, token_id: str) -> None:
        """Moves a token for the current player based on the rolled dice."""
        if game_state.status != GameStatus.IN_PROGRESS:
            raise ValueError("Game is not in progress")
        if game_state.dice_value is None:
            raise ValueError("Must roll dice first")

        current_color = game_state.current_turn
        player = game_state.players[current_color]
        
        # Find token
        token_to_move = next((t for t in player.tokens if t.id == token_id), None)
        if not token_to_move:
            raise ValueError("Token not found")

        # Validate move
        if not RulesEngine.is_valid_move(game_state, token_to_move, game_state.dice_value):
            raise ValueError("Invalid move")

        # Execute move
        if token_to_move.status == TokenStatus.BASE:
            token_to_move.status = TokenStatus.ACTIVE
            token_to_move.position = 0
            game_state.last_action = f"Player {current_color.value} entered board with token {token_id}."
        else:
            token_to_move.position += game_state.dice_value
            if token_to_move.position == 56:
                token_to_move.status = TokenStatus.FINISHED
                game_state.last_action = f"Player {current_color.value} finished with token {token_id}!"
            else:
                game_state.last_action = f"Player {current_color.value} moved token {token_id} to {token_to_move.position}."

        # Check for capture
        captured_token = RulesEngine.check_capture(game_state, token_to_move)
        if captured_token:
            captured_token.status = TokenStatus.BASE
            captured_token.position = -1
            game_state.last_action += f" Captured {captured_token.color.value} token!"

        # Clear movable tokens after move
        game_state.movable_tokens = []

        # Check win condition
        if RulesEngine.check_win_condition(game_state, current_color):
            game_state.status = GameStatus.FINISHED
            game_state.winner = current_color
            game_state.last_action += f" Player {current_color.value} wins!"
            return

        # Advance turn
        if (game_state.config.bonus_turn_on_six and game_state.dice_value == 6) or \
           (game_state.config.bonus_turn_on_capture and captured_token is not None):
            game_state.dice_value = None # Reset dice for extra roll
            game_state.last_action += " Extra turn!"
        else:
            GameEngine.next_turn(game_state)

    @staticmethod
    def next_turn(game_state: GameState) -> None:
        """Advances the game to the next player's turn."""
        game_state.dice_value = None
        game_state.consecutive_sixes = 0

        current_idx = game_state.turn_order.index(game_state.current_turn)
        for i in range(1, 5):
            next_idx = (current_idx + i) % 4
            next_color = game_state.turn_order[next_idx]
            if next_color in game_state.players:
                game_state.current_turn = next_color
                break
        
        # Take snapshot for the new turn
        GameEngine.take_turn_snapshot(game_state)
