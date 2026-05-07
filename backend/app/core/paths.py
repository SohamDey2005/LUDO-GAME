from typing import List, Dict, Union
from app.models.game import Color

# Cell IDs are either integers (0-51) for the main perimeter
# or strings for home stretch and finish.

def get_full_path_for_color(color: Color) -> List[Union[int, str]]:
    """
    Returns the complete sequence of Cell IDs for a player's token journey.
    1. 51 Perimeter squares starting from START_SQUARES[color]
    2. 5 Home stretch squares
    3. 1 Finish square
    Total: 57 Cell IDs
    """
    start_idx = {
        Color.RED: 0,
        Color.GREEN: 13,
        Color.YELLOW: 26,
        Color.BLUE: 39
    }[color]
    
    # 51 Perimeter squares
    perimeter_path = [(start_idx + i) % 52 for i in range(51)]
    
    # 5 Home stretch squares
    home_stretch = [f"{color.value}_home_{i}" for i in range(5)]
    
    # Finish square
    finish = f"{color.value}_finish"
    
    return perimeter_path + home_stretch + [finish]

def get_absolute_cell_id(color: Color, position: int) -> Union[int, str]:
    """
    Converts a relative position (0-56) to a Cell ID.
    0-50: Perimeter
    51-55: Home stretch
    56: Finish
    -1: Base
    """
    if position == -1:
        return f"{color.value}_base"
    
    full_path = get_full_path_for_color(color)
    if 0 <= position < len(full_path):
        return full_path[position]
    
    return f"{color.value}_base" # Fallback
