from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from app.models.config import GameConfig


class Color(str, Enum):
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"


class PlayerType(str, Enum):
    HUMAN = "human"
    AI = "ai"


class TokenStatus(str, Enum):
    BASE = "base"
    ACTIVE = "active"
    FINISHED = "finished"


class Token(BaseModel):
    id: str
    color: Color
    position: int = -1  # -1 means in base, 0-50 main path, 51-55 home path, 56 finished
    status: TokenStatus = TokenStatus.BASE

    def get_absolute_position(self) -> int:
        """
        Returns the absolute position on the 52-square perimeter (0-51).
        Returns -1 if in base or in the home stretch.
        """
        if self.status != TokenStatus.ACTIVE or self.position > 50:
            return -1
            
        offset = {
            Color.RED: 0,
            Color.GREEN: 13,
            Color.YELLOW: 26,
            Color.BLUE: 39
        }
        return (self.position + offset[self.color]) % 52


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


class GameState(BaseModel):
    id: str
    config: GameConfig = Field(default_factory=GameConfig)
    players: Dict[Color, Player] = {}
    current_turn: Optional[Color] = None
    status: GameStatus = GameStatus.WAITING
    dice_value: Optional[int] = None
    consecutive_sixes: int = 0
    winner: Optional[Color] = None
    last_action: Optional[str] = None
    
    # Track the order of play
    turn_order: List[Color] = [Color.RED, Color.GREEN, Color.YELLOW, Color.BLUE]
