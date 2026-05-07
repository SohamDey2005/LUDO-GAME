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
    # 1, 14, 27, 40 are the 4 star-marked squares in the second image.
    safe_squares: List[int] = [1, 14, 27, 40]
