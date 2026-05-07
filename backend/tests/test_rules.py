"""
Comprehensive test suite for the Official Ludo Rule Engine (Rule 25).
Coverage target: 90%+

Run with: pytest tests/ -v
"""
import pytest
from app.core.config import GameSettings
from app.core.rules import DiceManager, MoveValidator, CaptureManager, TurnManager, WinConditionManager
from app.models.game import Color, GameState, GameStatus, Token, TokenStatus, Player, PlayerType
from app.services.game_engine import GameEngine


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_game(n_players: int = 4, **setting_kwargs) -> GameState:
    """Creates a fully started game with n_players human players."""
    settings = GameSettings(**setting_kwargs)
    game = GameEngine.create_game(settings)
    colors = [Color.RED, Color.GREEN, Color.YELLOW, Color.BLUE][:n_players]
    for c in colors:
        GameEngine.add_player(game, c.value, c, PlayerType.HUMAN)
    GameEngine.start_game(game)
    return game


def active_token(color: Color, position: int) -> Token:
    return Token(id=f"{color.value}_t", color=color, position=position, status=TokenStatus.ACTIVE)


def base_token(color: Color) -> Token:
    return Token(id=f"{color.value}_b", color=color, position=-1, status=TokenStatus.BASE)


def finished_token(color: Color) -> Token:
    return Token(id=f"{color.value}_f", color=color, position=56, status=TokenStatus.FINISHED)


# ─────────────────────────────────────────────────────────────────────────────
# Rule 2 & 4 — Initial Token State / Entering the Board
# ─────────────────────────────────────────────────────────────────────────────

class TestEnteringTheBoard:
    def test_base_token_needs_six(self):
        game = make_game()
        token = base_token(Color.RED)
        for v in range(1, 6):
            assert not MoveValidator.is_valid(game, token, v), f"Should reject dice={v} for base token"

    def test_base_token_accepts_six(self):
        game = make_game()
        token = base_token(Color.RED)
        assert MoveValidator.is_valid(game, token, 6)

    def test_enter_board_sets_position_zero(self):
        game = make_game()
        game.dice_value = 6
        token_id = game.players[Color.RED].tokens[0].id
        GameEngine.move_token(game, token_id)
        t = game.players[Color.RED].tokens[0]
        assert t.status == TokenStatus.ACTIVE
        assert t.position == 0

    def test_all_tokens_base_non_six_auto_passes_turn(self):
        """Rule 4 + 15: No tokens on board and roll != 6 → turn must pass."""
        game = make_game()
        game.dice_value = 3
        valid = MoveValidator.get_valid_tokens(game, Color.RED, 3)
        assert valid == []


# ─────────────────────────────────────────────────────────────────────────────
# Rule 6 — Three Consecutive Sixes
# ─────────────────────────────────────────────────────────────────────────────

class TestConsecutiveSixes:
    def test_two_sixes_no_forfeit(self):
        game = make_game()
        game.consecutive_sixes = 2
        forfeit = DiceManager.handle_consecutive_sixes(game, 5)
        assert not forfeit
        assert game.consecutive_sixes == 0  # reset on non-six

    def test_third_six_forfeits_turn(self):
        game = make_game()
        game.consecutive_sixes = 2
        forfeit = DiceManager.handle_consecutive_sixes(game, 6)
        assert forfeit
        assert game.consecutive_sixes == 0  # reset after forfeit

    def test_three_sixes_via_roll_dice(self):
        game = make_game()
        # Place a token on board so we'd normally have valid moves
        game.players[Color.RED].tokens[0].status = TokenStatus.ACTIVE
        game.players[Color.RED].tokens[0].position = 5
        game.consecutive_sixes = 2
        import unittest.mock as mock
        with mock.patch("app.core.rules.DiceManager.roll", return_value=6):
            GameEngine.roll_dice(game)
        # Turn should have passed to GREEN
        assert game.current_turn == Color.GREEN
        assert game.dice_value is None

    def test_configurable_consecutive_limit(self):
        """Rule 24: consecutive_six_limit should be configurable."""
        game = make_game(consecutive_six_limit=2)
        game.consecutive_sixes = 1
        forfeit = DiceManager.handle_consecutive_sixes(game, 6)
        assert forfeit  # Limit is 2, so 2nd six forfeits


# ─────────────────────────────────────────────────────────────────────────────
# Rule 8 — Valid Move Detection / Movement
# ─────────────────────────────────────────────────────────────────────────────

class TestMovementValidation:
    def test_finished_token_cannot_move(self):
        game = make_game()
        token = finished_token(Color.RED)
        assert not MoveValidator.is_valid(game, token, 3)

    def test_active_token_normal_move(self):
        game = make_game()
        token = active_token(Color.RED, 10)
        assert MoveValidator.is_valid(game, token, 5)

    def test_active_token_exact_finish(self):
        game = make_game()
        token = active_token(Color.RED, 53)
        assert MoveValidator.is_valid(game, token, 3)  # 53+3=56, exact home

    def test_active_token_overshoot_invalid(self):
        """Rule 13: Cannot overshoot home cell."""
        game = make_game()
        token = active_token(Color.RED, 54)
        assert not MoveValidator.is_valid(game, token, 5)  # 54+5=59 > 56

    def test_no_valid_move_auto_passes(self):
        """Rule 15: Auto-pass when no legal move exists."""
        import unittest.mock as mock
        game = make_game()
        # Token at 54, must roll exactly 2; roll 5 instead
        game.players[Color.RED].tokens[0].status = TokenStatus.ACTIVE
        game.players[Color.RED].tokens[0].position = 54
        for t in game.players[Color.RED].tokens[1:]:
            t.status = TokenStatus.FINISHED
            t.position = 56
        with mock.patch("app.core.rules.DiceManager.roll", return_value=5):
            GameEngine.roll_dice(game)
        # Turn passed because no valid moves
        assert game.current_turn == Color.GREEN


# ─────────────────────────────────────────────────────────────────────────────
# Rule 9 — Safe Zones
# ─────────────────────────────────────────────────────────────────────────────

class TestSafeZones:
    def test_token_on_safe_zone_not_captured(self):
        game = make_game()
        # Green token at perimeter pos 0 (RED's starting square, a safe zone)
        # RED's offset is 0, so absolute pos 0 = RED token at position 0
        # GREEN's offset is 13, so GREEN at position 39 => absolute (39+13)%52 = 0
        green_token = active_token(Color.GREEN, 39)
        game.players[Color.GREEN].tokens[0] = green_token

        red_token = active_token(Color.RED, 0)  # absolute pos = 0 (safe zone)
        # Simulate red token landing on absolute pos 0 — it is a safe zone
        result = CaptureManager.check_capture(game, red_token)
        assert result is None, "Tokens on safe zones must not be captured"

    def test_token_off_safe_zone_can_be_captured(self):
        game = make_game()
        # Place a green token at absolute pos 5 (not a safe zone)
        # GREEN offset=13; pos 5 → abs = (5+13)%52 = 18. Not in safe_zones.
        green_token = active_token(Color.GREEN, 5)
        game.players[Color.GREEN].tokens[0] = green_token

        # Place red token that lands on same absolute pos 18: RED offset=0, pos=18
        red_token = active_token(Color.RED, 18)
        result = CaptureManager.check_capture(game, red_token)
        assert result is not None, "Token not on safe zone should be capturable"

    def test_configurable_safe_zones(self):
        """Rule 24: Safe zones should be configurable."""
        # Empty safe zones — no protection anywhere
        game = make_game(safe_zones=[])
        green_token = active_token(Color.GREEN, 39)  # normally on safe zone 0
        game.players[Color.GREEN].tokens[0] = green_token
        red_token = active_token(Color.RED, 0)  # abs pos 0, now NOT safe
        # Should be captured since safe_zones is empty
        result = CaptureManager.check_capture(game, red_token)
        assert result is not None


# ─────────────────────────────────────────────────────────────────────────────
# Rule 10 — Token Stacking / Blocking
# ─────────────────────────────────────────────────────────────────────────────

class TestBlocking:
    def _game_with_green_block(self, position: int) -> GameState:
        """Puts 2 GREEN tokens at the given position to form a block."""
        game = make_game()
        for i in range(2):
            game.players[Color.GREEN].tokens[i].status = TokenStatus.ACTIVE
            game.players[Color.GREEN].tokens[i].position = position
        return game

    def test_block_prevents_passing(self):
        """RED token cannot pass through a GREEN block on its path."""
        # GREEN block at logical pos 26 → abs = (26+13)%52 = 39
        # RED token at pos 35 → abs = 35. Roll=5 → passes through abs 36,37,38,39(block),40
        game = self._game_with_green_block(26)
        red_token = active_token(Color.RED, 35)
        assert not MoveValidator.is_valid(game, red_token, 5)

    def test_block_prevents_landing(self):
        """RED token cannot land on a GREEN block square."""
        game = self._game_with_green_block(26)
        # RED at pos 30, roll=9 → lands on abs 39 (GREEN block)
        red_token = active_token(Color.RED, 30)
        assert not MoveValidator.is_valid(game, red_token, 9)

    def test_block_not_capturable(self):
        """A block of 2+ tokens is immune to capture."""
        game = self._game_with_green_block(5)
        # GREEN at pos 5 → abs = (5+13)%52 = 18
        red_token = active_token(Color.RED, 18)
        assert CaptureManager.check_capture(game, red_token) is None

    def test_single_token_is_capturable(self):
        """Single token (not a block) CAN be captured."""
        game = make_game()
        game.players[Color.GREEN].tokens[0].status = TokenStatus.ACTIVE
        game.players[Color.GREEN].tokens[0].position = 5  # abs = 18
        red_token = active_token(Color.RED, 18)
        result = CaptureManager.check_capture(game, red_token)
        assert result is not None

    def test_stacking_can_be_disabled(self):
        """Rule 24: Blocking should be disabled when enable_stacking_block=False."""
        game = make_game(enable_stacking_block=False)
        for i in range(2):
            game.players[Color.GREEN].tokens[i].status = TokenStatus.ACTIVE
            game.players[Color.GREEN].tokens[i].position = 26
        red_token = active_token(Color.RED, 35)
        # Without blocking, RED can pass through
        assert MoveValidator.is_valid(game, red_token, 5)


# ─────────────────────────────────────────────────────────────────────────────
# Rule 11 — Capturing Grants Extra Turn
# ─────────────────────────────────────────────────────────────────────────────

class TestCapture:
    def test_capture_grants_extra_turn(self):
        game = make_game()
        # Put RED token at pos 18 (abs=18), GREEN token at abs 18 too
        game.players[Color.RED].tokens[0].status = TokenStatus.ACTIVE
        game.players[Color.RED].tokens[0].position = 15  # will move +3 to 18
        game.players[Color.GREEN].tokens[0].status = TokenStatus.ACTIVE
        game.players[Color.GREEN].tokens[0].position = 5  # abs = 18 ← same cell
        game.dice_value = 3
        game.valid_move_ids = [game.players[Color.RED].tokens[0].id]

        GameEngine.move_token(game, game.players[Color.RED].tokens[0].id)

        # RED should still have the turn (extra turn from capture)
        assert game.current_turn == Color.RED
        assert game.dice_value is None  # dice reset for extra roll

    def test_captured_token_returns_to_base(self):
        game = make_game()
        green_tok = game.players[Color.GREEN].tokens[0]
        green_tok.status = TokenStatus.ACTIVE
        green_tok.position = 5  # abs=18

        captured = CaptureManager.check_capture(game, active_token(Color.RED, 18))
        assert captured is not None
        CaptureManager.execute_capture(game, captured)
        assert captured.status == TokenStatus.BASE
        assert captured.position == -1

    def test_capture_history_updated(self):
        game = make_game()
        green_tok = game.players[Color.GREEN].tokens[0]
        green_tok.status = TokenStatus.ACTIVE
        green_tok.position = 5  # abs=18
        CaptureManager.execute_capture(game, green_tok)
        assert green_tok.id in game.capture_history


# ─────────────────────────────────────────────────────────────────────────────
# Rule 14 — Win Condition
# ─────────────────────────────────────────────────────────────────────────────

class TestWinCondition:
    def test_win_requires_all_four_tokens(self):
        game = make_game()
        for t in game.players[Color.RED].tokens[:3]:
            t.status = TokenStatus.FINISHED
            t.position = 56
        assert not WinConditionManager.check(game, Color.RED)

    def test_all_four_finished_wins(self):
        game = make_game()
        for t in game.players[Color.RED].tokens:
            t.status = TokenStatus.FINISHED
            t.position = 56
        assert WinConditionManager.check(game, Color.RED)

    def test_win_finalises_game(self):
        game = make_game()
        for t in game.players[Color.RED].tokens:
            t.status = TokenStatus.FINISHED
            t.position = 56
        WinConditionManager.finalise(game, Color.RED)
        assert game.status == GameStatus.FINISHED
        assert game.winner == Color.RED

    def test_last_token_exact_roll_triggers_win(self):
        """Rule 13+14: Exact roll finishing last token should immediately win."""
        game = make_game()
        for t in game.players[Color.RED].tokens[:3]:
            t.status = TokenStatus.FINISHED
            t.position = 56
        game.players[Color.RED].tokens[3].status = TokenStatus.ACTIVE
        game.players[Color.RED].tokens[3].position = 53  # needs exactly 3
        game.dice_value = 3
        game.valid_move_ids = [game.players[Color.RED].tokens[3].id]
        GameEngine.move_token(game, game.players[Color.RED].tokens[3].id)
        assert game.status == GameStatus.FINISHED
        assert game.winner == Color.RED


# ─────────────────────────────────────────────────────────────────────────────
# Rule 5 — Turn System / Extra Turn on Six
# ─────────────────────────────────────────────────────────────────────────────

class TestTurnSystem:
    def test_rolling_six_grants_extra_turn(self):
        import unittest.mock as mock
        game = make_game()
        # Give RED an active token so a move exists
        game.players[Color.RED].tokens[0].status = TokenStatus.ACTIVE
        game.players[Color.RED].tokens[0].position = 5
        with mock.patch("app.core.rules.DiceManager.roll", return_value=6):
            GameEngine.roll_dice(game)
        game.dice_value = 6
        GameEngine.move_token(game, game.players[Color.RED].tokens[0].id)
        assert game.current_turn == Color.RED  # Still RED's turn

    def test_normal_roll_advances_turn(self):
        import unittest.mock as mock
        game = make_game()
        game.players[Color.RED].tokens[0].status = TokenStatus.ACTIVE
        game.players[Color.RED].tokens[0].position = 5
        with mock.patch("app.core.rules.DiceManager.roll", return_value=3):
            GameEngine.roll_dice(game)
        GameEngine.move_token(game, game.players[Color.RED].tokens[0].id)
        assert game.current_turn == Color.GREEN

    def test_turn_order_wraps_around(self):
        """After BLUE, turn returns to RED."""
        game = make_game()
        game.current_turn = Color.BLUE
        game.players[Color.BLUE].tokens[0].status = TokenStatus.ACTIVE
        game.players[Color.BLUE].tokens[0].position = 5
        game.dice_value = 3
        GameEngine.move_token(game, game.players[Color.BLUE].tokens[0].id)
        assert game.current_turn == Color.RED

    def test_two_player_turn_skips_missing(self):
        """In a 2-player game, turns should only alternate between those 2 colors."""
        game = make_game(n_players=2)  # RED and GREEN only
        game.players[Color.RED].tokens[0].status = TokenStatus.ACTIVE
        game.players[Color.RED].tokens[0].position = 5
        game.dice_value = 2
        GameEngine.move_token(game, game.players[Color.RED].tokens[0].id)
        assert game.current_turn == Color.GREEN


# ─────────────────────────────────────────────────────────────────────────────
# Rule 18 — Anti-Cheat Validation
# ─────────────────────────────────────────────────────────────────────────────

class TestAntiCheat:
    def test_reject_move_before_roll(self):
        game = make_game()
        game.players[Color.RED].tokens[0].status = TokenStatus.ACTIVE
        game.players[Color.RED].tokens[0].position = 5
        with pytest.raises(ValueError, match="Must roll dice"):
            GameEngine.move_token(game, game.players[Color.RED].tokens[0].id)

    def test_reject_second_roll_same_turn(self):
        game = make_game()
        game.dice_value = 3
        with pytest.raises(ValueError, match="Dice already rolled"):
            GameEngine.roll_dice(game)

    def test_reject_wrong_color_token(self):
        game = make_game()
        game.dice_value = 6
        # Try to move a GREEN token when it's RED's turn
        green_token_id = game.players[Color.GREEN].tokens[0].id
        with pytest.raises(ValueError):
            GameEngine.move_token(game, green_token_id)

    def test_reject_move_on_finished_game(self):
        game = make_game()
        game.status = GameStatus.FINISHED
        with pytest.raises(ValueError, match="not in progress"):
            GameEngine.roll_dice(game)

    def test_reject_overshoot_move(self):
        """Backend must reject a move that overshoots home."""
        game = make_game()
        tok = game.players[Color.RED].tokens[0]
        tok.status = TokenStatus.ACTIVE
        tok.position = 54  # needs exactly 2 to win
        game.dice_value = 5  # would overshoot
        with pytest.raises(ValueError, match="Illegal move"):
            GameEngine.move_token(game, tok.id)


# ─────────────────────────────────────────────────────────────────────────────
# Rule 19 — History Tracking
# ─────────────────────────────────────────────────────────────────────────────

class TestHistory:
    def test_dice_history_recorded(self):
        import unittest.mock as mock
        game = make_game()
        game.players[Color.RED].tokens[0].status = TokenStatus.ACTIVE
        game.players[Color.RED].tokens[0].position = 5
        with mock.patch("app.core.rules.DiceManager.roll", return_value=4):
            GameEngine.roll_dice(game)
        assert 4 in game.dice_history

    def test_move_history_recorded(self):
        game = make_game()
        tok = game.players[Color.RED].tokens[0]
        tok.status = TokenStatus.ACTIVE
        tok.position = 10
        game.dice_value = 3
        GameEngine.move_token(game, tok.id)
        assert len(game.move_history) == 1
        record = game.move_history[0]
        assert record.player == Color.RED
        assert record.from_pos == 10
        assert record.to_pos == 13
        assert record.dice == 3
