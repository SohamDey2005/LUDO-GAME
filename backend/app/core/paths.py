from typing import List, Dict, Union
from app.models.game import Color

# Aligned with LudoBoardScene.ts (Clockwise from Top-Left Red)
START_SQUARES = {
    Color.RED: 0,
    Color.BLUE: 13,
    Color.YELLOW: 26,
    Color.GREEN: 39
}

def get_full_path_for_color(color: Color) -> List[Union[int, str]]:
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
