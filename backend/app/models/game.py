"""
Core game state models (Rules 1, 2, 19).
All models are Pydantic-based for JSON serialization and anti-cheat validation.
"""
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from app.core.config import GameSettings


class Color(str, Enum):
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"


class PlayerType(str, Enum):
    HUMAN = "human"
    AI = "ai"


class TokenStatus(str, Enum):
    BASE = "base"          # In the home base, not yet on the board
    ACTIVE = "active"      # On the main board path or home column
    FINISHED = "finished"  # Reached the final home cell


# Color offsets on the 52-square perimeter. Each color starts 13 squares apart.
COLOR_OFFSETS: Dict[Color, int] = {
    Color.RED: 0,
    Color.GREEN: 13,
    Color.YELLOW: 26,
    Color.BLUE: 39,
}


class Token(BaseModel):
    """
    Represents a single player token.
    position:
        -1  = in base (BASE status)
        0   = just entered the board (starting square)
        1-50 = on the main 52-square perimeter path
        51-55 = on the player's personal home column (home stretch)
        56  = final home cell (FINISHED status)
    """
    id: str
    color: Color
    position: int = -1
    status: TokenStatus = TokenStatus.BASE

    def get_absolute_position(self) -> int:
        """
        Returns the absolute 0-51 perimeter position for collision/capture checks.
        Returns -1 if in base, finished, or inside the home column (pos > 50).
        """
        return self._abs_at(self.position)

    def get_absolute_position_at(self, pos: int) -> int:
        """
        Returns the absolute perimeter position IF this token were at the given
        logical position. Used for path-blocking checks during move validation.
        Returns -1 if pos is in the home stretch (> 50).
        """
        return self._abs_at(pos)

    def _abs_at(self, pos: int) -> int:
        if pos < 0 or pos > 50:
            return -1
        offset = COLOR_OFFSETS[self.color]
        return (pos + offset) % 52


class Player(BaseModel):
    id: str
    name: str
    color: Color
    player_type: PlayerType
    tokens: List[Token] = []


class GameStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class MoveRecord(BaseModel):
    """Records a single move for history (Rule 19)."""
    turn: int
    player: Color
    token_id: str
    from_pos: int
    to_pos: int
    dice: int
    captured: Optional[str] = None  # captured token id, if any


class GameState(BaseModel):
    """
    Single source of truth for all game data (Rules 16, 19, 20).
    This object is persisted to disk and broadcast via WebSockets.
    """
    id: str
    players: Dict[Color, Player] = {}
    current_turn: Optional[Color] = None
    status: GameStatus = GameStatus.WAITING
    dice_value: Optional[int] = None
    consecutive_sixes: int = 0
    winner: Optional[Color] = None
    last_action: Optional[str] = None
    turn_number: int = 0

    # History (Rule 19)
    dice_history: List[int] = []
    move_history: List[MoveRecord] = []
    capture_history: List[str] = []  # list of captured token ids

    # Valid moves for the current roll (sent to frontend for highlighting only)
    valid_move_ids: List[str] = []

    # Turn order — standard Ludo: Red → Green → Yellow → Blue
    turn_order: List[Color] = [Color.RED, Color.GREEN, Color.YELLOW, Color.BLUE]

    # Per-game configurable settings (Rule 24)
    settings: GameSettings = Field(default_factory=GameSettings)
