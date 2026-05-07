from typing import List, Optional, Union, Dict
from app.models.game import GameState, Token, Color, TokenStatus
from app.core.paths import get_absolute_cell_id, get_full_path_for_color

SAFE_SQUARES_ABSOLUTE = [0, 8, 13, 21, 26, 34, 39, 47]

class RulesEngine:
    @staticmethod
    def get_valid_moves(game_state: GameState, player_color: Color, dice_value: int) -> List[Token]:
        valid_tokens = []
        player = game_state.players.get(player_color)
        if not player:
            return valid_tokens

        for token in player.tokens:
            if RulesEngine.is_valid_move(game_state, token, dice_value):
                valid_tokens.append(token)
                
        return valid_tokens

    @staticmethod
    def is_valid_move(game_state: GameState, token: Token, dice_value: int) -> bool:
        if token.status == TokenStatus.FINISHED:
            return False

        if token.status == TokenStatus.BASE:
            if dice_value != 6:
                return False
            # Check if start square is blocked
            start_cell_id = get_absolute_cell_id(token.color, 0)
            if RulesEngine.is_cell_blocked(game_state, start_cell_id, token.color):
                return False
            return True

        if token.status == TokenStatus.ACTIVE:
            projected_pos = token.position + dice_value
            if projected_pos > 56:
                return False # Rule 13: Exact roll to finish

            # Rule 10: Check if path is blocked
            if game_state.config.stack_blocks_movement:
                if RulesEngine.is_path_blocked(game_state, token, dice_value):
                    return False

            # Check if destination is a block of another player
            dest_cell_id = get_absolute_cell_id(token.color, projected_pos)
            if RulesEngine.is_cell_blocked(game_state, dest_cell_id, token.color):
                return False

            return True
            
        return False

    @staticmethod
    def is_path_blocked(game_state: GameState, token: Token, dice_value: int) -> bool:
        """Rule 10: Opponent tokens cannot pass through the block."""
        full_path = get_full_path_for_color(token.color)
        
        # Check every square on the path except the starting square
        for i in range(1, dice_value + 1):
            check_pos = token.position + i
            if check_pos > 56:
                break
            
            cell_id = full_path[check_pos]
            if RulesEngine.is_cell_blocked(game_state, cell_id, token.color):
                # If we land on it, is_cell_blocked already handles if it's our own block
                # But Rule 10 says "cannot pass through", so if it's an opponent block, we are blocked.
                return True
        return False

    @staticmethod
    def is_cell_blocked(game_state: GameState, cell_id: Union[int, str], moving_player_color: Color) -> bool:
        """A cell is blocked if it has 2+ tokens of a SINGLE opponent color."""
        # Perimeter indices (0-51) are the only ones that can be blocked usually, 
        # but let's be generic.
        
        # Safe zones allow multiple players but Rule 10 says blocks block movement.
        # "multiple players may occupy safe zones" (Rule 9)
        
        tokens_on_cell = RulesEngine.get_tokens_on_cell(game_state, cell_id)
        
        # Group by color
        counts: Dict[Color, int] = {}
        for t in tokens_on_cell:
            counts[t.color] = counts.get(t.color, 0) + 1
            
        for color, count in counts.items():
            if color != moving_player_color and count >= 2:
                return True
        return False

    @staticmethod
    def get_tokens_on_cell(game_state: GameState, cell_id: Union[int, str]) -> List[Token]:
        tokens = []
        for player in game_state.players.values():
            for token in player.tokens:
                if get_absolute_cell_id(token.color, token.position) == cell_id:
                    tokens.append(token)
        return tokens

    @staticmethod
    def check_capture(game_state: GameState, moving_token: Token) -> Optional[Token]:
        """Rule 11: Capture logic with stack and safe zone immunity."""
        cell_id = get_absolute_cell_id(moving_token.color, moving_token.position)
        
        # Rule 9: Safe zones prevent capture
        if game_state.config.safe_zones_enabled:
            if isinstance(cell_id, int) and cell_id in game_state.config.safe_squares:
                return None

        # Home stretch is naturally safe (only same color can enter)
        if isinstance(cell_id, str) and "home" in cell_id:
            return None

        tokens_on_cell = RulesEngine.get_tokens_on_cell(game_state, cell_id)
        
        # Rule 10: Cannot capture a block (2+ tokens)
        # Find opponent tokens on this cell
        opponents = [t for t in tokens_on_cell if t.color != moving_token.color]
        
        if not opponents:
            return None
            
        # If there's more than one opponent token of the same color, it's a block
        color_counts: Dict[Color, int] = {}
        for t in opponents:
            color_counts[t.color] = color_counts.get(t.color, 0) + 1
            
        # We can only capture if the count for that color is 1
        # In Ludo, usually you land on ONE token. If there are 2, you are blocked from landing.
        # So if we are here, it means we legally landed.
        # If we landed on a cell with 1 opponent token, we capture it.
        
        target_token = opponents[0]
        if color_counts[target_token.color] == 1:
            return target_token
            
        return None

    @staticmethod
    def check_win_condition(game_state: GameState, player_color: Color) -> bool:
        player = game_state.players.get(player_color)
        if not player:
            return False
        return all(token.status == TokenStatus.FINISHED for token in player.tokens)
