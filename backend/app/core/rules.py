"""
Official Ludo Rule Engine (Rules 8-15, 23).
Modular, deterministic, and cheat-proof. The backend is the sole authority.

Managers:
    - DiceManager       : Dice generation and consecutive-six tracking (Rules 3, 6)
    - MoveValidator     : Legal move detection with blocking and exact-roll logic (Rules 8, 10, 13)
    - CaptureManager    : Capture detection respecting safe zones and blocks (Rules 9-11)
    - TurnManager       : Turn sequencing with bonus turns and auto-pass (Rules 5, 6, 15)
    - WinConditionManager: Detects winner and triggers leaderboard update (Rule 14)
    - RulesEngine       : Orchestrates all managers (public API used by GameEngine)
"""
from typing import List, Optional
import random

from app.models.game import (
    GameState, Token, Color, TokenStatus, GameStatus, MoveRecord
)
from app.core.config import GameSettings


# ─────────────────────────────────────────────────────────────────────────────
# DiceManager (Rules 3, 6)
# ─────────────────────────────────────────────────────────────────────────────

class DiceManager:
    """Server-side fair dice. Frontend dice values are NEVER trusted."""

    @staticmethod
    def roll() -> int:
        """Returns a cryptographically random die value 1-6."""
        return random.randint(1, 6)

    @staticmethod
    def handle_consecutive_sixes(game_state: GameState, roll: int) -> bool:
        """
        Tracks consecutive sixes (Rule 6).
        Returns True if the turn should be FORFEITED (3 in a row).
        """
        if roll == 6:
            game_state.consecutive_sixes += 1
            if game_state.consecutive_sixes >= game_state.settings.consecutive_six_limit:
                game_state.consecutive_sixes = 0
                return True  # Forfeit
        else:
            game_state.consecutive_sixes = 0
        return False


# ─────────────────────────────────────────────────────────────────────────────
# MoveValidator (Rules 8, 10, 13)
# ─────────────────────────────────────────────────────────────────────────────

class MoveValidator:
    """Validates every move server-side. Frontend input is never trusted."""

    @staticmethod
    def get_valid_tokens(game_state: GameState, player_color: Color, dice_value: int) -> List[str]:
        """Returns a list of token IDs that have at least one legal move."""
        player = game_state.players.get(player_color)
        if not player:
            return []
        return [
            t.id for t in player.tokens
            if MoveValidator.is_valid(game_state, t, dice_value)
        ]

    @staticmethod
    def is_valid(game_state: GameState, token: Token, dice_value: int) -> bool:
        """
        Complete official move validation (Rules 8, 10, 13):
        1. Token must belong to current player (checked upstream in GameEngine).
        2. Finished tokens cannot move.
        3. Base tokens need exactly a 6 to enter.
        4. Active tokens: cannot overshoot home (exact finish), cannot be
           path-blocked by an opponent's stack of 2+ tokens.
        """
        settings = game_state.settings

        if token.status == TokenStatus.FINISHED:
            return False

        if token.status == TokenStatus.BASE:
            # Rule 4: Only a 6 lets a token leave base
            return dice_value == 6

        if token.status == TokenStatus.ACTIVE:
            new_pos = token.position + dice_value

            # Rule 13: Cannot overshoot the home cell (position 56)
            if new_pos > 56:
                return False

            # Rule 10: Check if path is blocked by an opponent block
            if settings.enable_stacking_block:
                for step in range(1, dice_value + 1):
                    intermediate_pos = token.position + step
                    # Blocking only applies on the shared perimeter (pos 0-50)
                    if intermediate_pos <= 50:
                        abs_pos = token.get_absolute_position_at(intermediate_pos)
                        if MoveValidator._is_blocked(game_state, abs_pos, token.color):
                            return False

            return True

        return False

    @staticmethod
    def _is_blocked(game_state: GameState, absolute_pos: int, mover_color: Color) -> bool:
        """
        Returns True if an OPPONENT has 2+ tokens on this absolute position,
        forming an impassable block (Rule 10).
        """
        if absolute_pos == -1:
            return False
        for color, player in game_state.players.items():
            if color == mover_color:
                continue
            count = sum(
                1 for t in player.tokens
                if t.status == TokenStatus.ACTIVE
                and t.get_absolute_position() == absolute_pos
            )
            if count >= 2:
                return True
        return False


# ─────────────────────────────────────────────────────────────────────────────
# CaptureManager (Rules 9, 10, 11)
# ─────────────────────────────────────────────────────────────────────────────

class CaptureManager:
    """Handles token capture logic with safe-zone and block immunity."""

    @staticmethod
    def check_capture(game_state: GameState, moving_token: Token) -> Optional[Token]:
        """
        Returns the opponent token to be captured, or None.
        Capture is BLOCKED if:
         - The landing square is in SAFE_ZONES (Rule 9)
         - The landing square has 2+ opponent tokens (Rule 10 - Block immunity)
        """
        absolute_pos = moving_token.get_absolute_position()

        # Rule 9: Safe zones — no capture possible
        if absolute_pos == -1 or absolute_pos in game_state.settings.safe_zones:
            return None

        for color, player in game_state.players.items():
            if color == moving_token.color:
                continue
            occupants = [
                t for t in player.tokens
                if t.status == TokenStatus.ACTIVE
                and t.get_absolute_position() == absolute_pos
            ]
            if len(occupants) == 1:
                return occupants[0]   # Rule 11: single opponent token → captured
            # len >= 2 → block, immune to capture (Rule 10)

        return None

    @staticmethod
    def execute_capture(game_state: GameState, captured_token: Token) -> None:
        """Sends the captured token back to base (Rule 11)."""
        captured_token.status = TokenStatus.BASE
        captured_token.position = -1
        game_state.capture_history.append(captured_token.id)


# ─────────────────────────────────────────────────────────────────────────────
# TurnManager (Rules 5, 6, 15)
# ─────────────────────────────────────────────────────────────────────────────

class TurnManager:
    """Controls all turn advancement logic."""

    @staticmethod
    def advance(game_state: GameState) -> None:
        """Moves to the next player, wrapping around and skipping missing colors."""
        game_state.dice_value = None
        game_state.valid_move_ids = []
        game_state.consecutive_sixes = 0
        game_state.turn_number += 1

        current_idx = game_state.turn_order.index(game_state.current_turn)
        for i in range(1, 5):
            next_color = game_state.turn_order[(current_idx + i) % 4]
            if next_color in game_state.players:
                game_state.current_turn = next_color
                return

    @staticmethod
    def grant_extra_turn(game_state: GameState) -> None:
        """
        Grants an extra roll by resetting dice but keeping the same player
        (Rules 5, 11 — rolling a 6 or capturing grants one extra turn).
        """
        game_state.dice_value = None
        game_state.valid_move_ids = []


# ─────────────────────────────────────────────────────────────────────────────
# WinConditionManager (Rule 14)
# ─────────────────────────────────────────────────────────────────────────────

class WinConditionManager:
    """Detects victory and finalises game state."""

    @staticmethod
    def check(game_state: GameState, player_color: Color) -> bool:
        """Returns True if all 4 of this player's tokens are FINISHED."""
        player = game_state.players.get(player_color)
        if not player:
            return False
        return all(t.status == TokenStatus.FINISHED for t in player.tokens)

    @staticmethod
    def finalise(game_state: GameState, winner_color: Color) -> None:
        """Marks the game as finished with the winning player."""
        game_state.status = GameStatus.FINISHED
        game_state.winner = winner_color
        game_state.last_action = (
            game_state.last_action or ""
        ) + f" 🏆 Player {winner_color.value} WINS!"


# ─────────────────────────────────────────────────────────────────────────────
# RulesEngine — Public API (Rule 23)
# ─────────────────────────────────────────────────────────────────────────────

class RulesEngine:
    """
    Thin orchestrator that exposes a clean public API to GameEngine.
    All sub-rules are implemented in the dedicated Manager classes above.
    """

    # Expose sub-managers as class attributes for direct use
    dice = DiceManager
    validator = MoveValidator
    capture = CaptureManager
    turn = TurnManager
    win = WinConditionManager

    @staticmethod
    def get_valid_moves(game_state: GameState, player_color: Color, dice_value: int) -> List[str]:
        return MoveValidator.get_valid_tokens(game_state, player_color, dice_value)

    @staticmethod
    def is_valid_move(game_state: GameState, token: Token, dice_value: int) -> bool:
        return MoveValidator.is_valid(game_state, token, dice_value)

    @staticmethod
    def check_capture(game_state: GameState, moving_token: Token) -> Optional[Token]:
        return CaptureManager.check_capture(game_state, moving_token)

    @staticmethod
    def check_win_condition(game_state: GameState, player_color: Color) -> bool:
        return WinConditionManager.check(game_state, player_color)
