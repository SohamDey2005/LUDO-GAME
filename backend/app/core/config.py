"""
Configurable game settings (Rule 24).
These can be modified per game session or globally via environment variables.
"""
from pydantic import BaseModel


class GameSettings(BaseModel):
    """All optional rule configurations for a Ludo game session."""

    # Rule 10: If True, 2+ same-color tokens on a square form a block that opponents cannot pass through.
    enable_stacking_block: bool = True

    # Rule 11: If True, capturing an opponent's token grants an extra turn.
    capture_grants_extra_turn: bool = True

    # Rule 5: If True, rolling a 6 grants an extra turn (standard rule).
    six_grants_extra_turn: bool = True

    # Rule 6: Number of consecutive sixes to trigger a forfeit. Standard = 3.
    consecutive_six_limit: int = 3

    # Rule 9: Absolute board positions (0-51) that are safe zones.
    # Default: 4 starting squares + 4 star-marked squares (standard Ludo board).
    safe_zones: list[int] = [0, 8, 13, 21, 26, 34, 39, 47]

    # Rule 24 Fast Mode: Tokens start on the board (position 0) instead of base.
    fast_mode: bool = False


# Default settings singleton used when no custom config is provided
DEFAULT_SETTINGS = GameSettings()
