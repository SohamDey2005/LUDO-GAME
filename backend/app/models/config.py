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
    # Define which absolute squares are safe (0-51)
    # 2, 15, 28, 41 are the 4 star-marked squares in the final clockwise layout.
    safe_squares: List[int] = [2, 15, 28, 41]
