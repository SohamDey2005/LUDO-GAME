from typing import List, Dict, Union
from app.models.game import Color

# Cell IDs are either integers (0-51) for the main perimeter
# or strings for home stretch and finish.

# Aligned with LudoBoardScene.ts (Clockwise from Green)
START_SQUARES = {
    Color.GREEN: 0,
    Color.YELLOW: 13,
    Color.BLUE: 26,
    Color.RED: 39
}

def get_full_path_for_color(color: Color) -> List[Union[int, str]]:
    """
    Returns the complete sequence of Cell IDs for a player's token journey.
    """
    start_idx = START_SQUARES[color]
    
    # 51 Perimeter squares
    perimeter_path = [(start_idx + i) % 52 for i in range(51)]
    
    # 5 Home stretch squares
    home_stretch = [f"{color.value}_home_{i}" for i in range(5)]
    
    # Finish square
    finish = f"{color.value}_finish"
    
    return perimeter_path + home_stretch + [finish]

def get_absolute_cell_id(color: Color, position: int) -> Union[int, str]:
    if position == -1:
        return f"{color.value}_base"
    
    full_path = get_full_path_for_color(color)
    if 0 <= position < len(full_path):
        return full_path[position]
    
    return f"{color.value}_base"
