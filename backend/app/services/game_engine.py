"""
GameEngine — Orchestrates all game actions (Rules 1-22).
This is the authoritative backend controller. All moves go through here.
Anti-cheat: every action validates turn ownership, dice state, and token legality.
"""
from typing import Optional
import uuid

from app.models.game import (
    GameState, GameStatus, Color, Player, PlayerType,
    Token, TokenStatus, MoveRecord
)
from app.core.config import GameSettings
from app.core.rules import RulesEngine, DiceManager, MoveValidator, CaptureManager, TurnManager, WinConditionManager


class GameEngine:

    # ── Game Setup ────────────────────────────────────────────────────────────

    @staticmethod
    def create_game(settings: Optional[GameSettings] = None) -> GameState:
        """Initialises a new empty game session (Rule 19/20)."""
        return GameState(
            id=str(uuid.uuid4()),
            players={},
            status=GameStatus.WAITING,
            settings=settings or GameSettings(),
        )

    @staticmethod
    def add_player(game: GameState, name: str, color: Color, player_type: PlayerType) -> Player:
        """Adds a player with 4 base tokens (Rule 1, 2)."""
        if game.status != GameStatus.WAITING:
            raise ValueError("Game already started")
        if color in game.players:
            raise ValueError(f"Color {color.value} already taken")
        if len(game.players) >= 4:
            raise ValueError("Game is full")

        tokens = [Token(id=f"{color.value}_{i}", color=color) for i in range(4)]

        # Rule 24 Fast Mode: all tokens start on the board
        if game.settings.fast_mode:
            for t in tokens:
                t.status = TokenStatus.ACTIVE
                t.position = 0

        player = Player(id=str(uuid.uuid4()), name=name, color=color,
                        player_type=player_type, tokens=tokens)
        game.players[color] = player
        return player

    @staticmethod
    def start_game(game: GameState) -> None:
        """Starts the game, setting the first turn in Red→Green→Yellow→Blue order."""
        if len(game.players) < 2:
            raise ValueError("Need at least 2 players")
        game.status = GameStatus.IN_PROGRESS
        for color in game.turn_order:
            if color in game.players:
                game.current_turn = color
                break

    # ── Core Turn Actions ─────────────────────────────────────────────────────

    @staticmethod
    def roll_dice(game: GameState) -> int:
        """
        Server-side dice roll (Rules 3, 6, 15).
        Anti-cheat: rejects if dice already rolled this turn.
        Auto-passes turn when no valid moves exist.
        """
        if game.status != GameStatus.IN_PROGRESS:
            raise ValueError("Game is not in progress")
        if game.dice_value is not None:
            raise ValueError("Dice already rolled — move a token first")

        roll = DiceManager.roll()
        game.dice_value = roll
        game.dice_history.append(roll)
        game.last_action = f"Player {game.current_turn.value} rolled a {roll}."

        # Rule 6: Three consecutive sixes → forfeit entire turn
        forfeit = DiceManager.handle_consecutive_sixes(game, roll)
        if forfeit:
            game.last_action += " Three consecutive sixes! Turn forfeited."
            TurnManager.advance(game)
            return roll

        # Rule 15: Auto-pass if no valid moves exist
        valid = MoveValidator.get_valid_tokens(game, game.current_turn, roll)
        game.valid_move_ids = valid
        if not valid:
            game.last_action += " No valid moves. Turn passed automatically."
            TurnManager.advance(game)

        return roll

    @staticmethod
    def move_token(game: GameState, token_id: str) -> None:
        """
        Executes a validated token move (Rules 7-14).
        Anti-cheat guards:
          - Game must be IN_PROGRESS
          - Dice must have been rolled
          - Token must belong to the current player
          - Move must pass MoveValidator (blocking, exact-finish, etc.)
        """
        # ── Anti-cheat guards ──────────────────────────────────────────────
        if game.status != GameStatus.IN_PROGRESS:
            raise ValueError("Game is not in progress")
        if game.dice_value is None:
            raise ValueError("Must roll dice before moving")

        current_color = game.current_turn
        player = game.players.get(current_color)
        if not player:
            raise ValueError("Current player not found")

        # Rule 18: Validate token ownership
        token = next((t for t in player.tokens if t.id == token_id), None)
        if not token:
            raise ValueError("Token not found or does not belong to current player")

        # Rule 8: Validate move legality
        if not MoveValidator.is_valid(game, token, game.dice_value):
            raise ValueError("Illegal move rejected by server")

        # ── Execute move ───────────────────────────────────────────────────
        from_pos = token.position
        dice = game.dice_value

        if token.status == TokenStatus.BASE:
            # Rule 4: Enter the board on the starting square (position 0)
            token.status = TokenStatus.ACTIVE
            token.position = 0
            game.last_action = f"Player {current_color.value} entered the board!"
        else:
            token.position += dice
            if token.position == 56:
                # Rule 12/13: Exact roll reached home
                token.status = TokenStatus.FINISHED
                game.last_action = (
                    f"Player {current_color.value} token {token_id} reached home!"
                )
            else:
                game.last_action = (
                    f"Player {current_color.value} moved {token_id} "
                    f"from {from_pos} to {token.position}."
                )

        # ── Capture check ─────────────────────────────────────────────────
        captured_token = CaptureManager.check_capture(game, token)
        extra_turn = False

        if captured_token:
            CaptureManager.execute_capture(game, captured_token)
            game.last_action += f" Captured {captured_token.color.value} token!"
            if game.settings.capture_grants_extra_turn:
                extra_turn = True

        # ── Record move history ────────────────────────────────────────────
        game.move_history.append(MoveRecord(
            turn=game.turn_number,
            player=current_color,
            token_id=token_id,
            from_pos=from_pos,
            to_pos=token.position,
            dice=dice,
            captured=captured_token.id if captured_token else None,
        ))

        # ── Win condition ─────────────────────────────────────────────────
        if WinConditionManager.check(game, current_color):
            WinConditionManager.finalise(game, current_color)
            return

        # ── Turn advancement ──────────────────────────────────────────────
        # Priority: capture bonus > rolling a 6 > normal advance
        if extra_turn:
            game.last_action += " Bonus turn for capture!"
            TurnManager.grant_extra_turn(game)
        elif dice == 6 and game.settings.six_grants_extra_turn:
            game.last_action += " Extra turn for rolling 6!"
            TurnManager.grant_extra_turn(game)
        else:
            TurnManager.advance(game)

    # ── Utilities ─────────────────────────────────────────────────────────────

    @staticmethod
    def next_turn(game: GameState) -> None:
        """Public helper for AI engine and endpoint fallbacks."""
        TurnManager.advance(game)
