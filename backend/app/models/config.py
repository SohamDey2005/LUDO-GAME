from pydantic import BaseModel
from typing import List

class GameConfig(BaseModel):
    allow_stacking: bool = True
    stack_blocks_movement: bool = True
    three_sixes_forfeit: bool = True
    exact_roll_to_finish: bool = True
    bonus_turn_on_capture: bool = True
    bonus_turn_on_six: bool = True
    safe_zones_enabled: bool = True
    # Define which absolute squares are safe
    safe_squares: List[int] = [0, 8, 13, 21, 26, 34, 39, 47]
