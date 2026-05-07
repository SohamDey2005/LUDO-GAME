from typing import List, Tuple, Optional
from app.models.game import GameState, Token, Color, TokenStatus

SAFE_SQUARES_ABSOLUTE = {0, 8, 13, 21, 26, 34, 39, 47}

class RulesEngine:
    @staticmethod
    def get_valid_moves(game_state: GameState, player_color: Color, dice_value: int) -> List[Token]:
        """Returns a list of tokens that can make a valid move given the dice value."""
        valid_tokens = []
        player = game_state.players.get(player_color)
        if not player:
            return valid_tokens

        for token in player.tokens:
            if RulesEngine.is_valid_move(token, dice_value):
                valid_tokens.append(token)
                
        return valid_tokens

    @staticmethod
    def is_valid_move(token: Token, dice_value: int) -> bool:
        """Checks if a specific token can move with the given dice value."""
        if token.status == TokenStatus.FINISHED:
            return False

        if token.status == TokenStatus.BASE:
            return dice_value == 6

        if token.status == TokenStatus.ACTIVE:
            projected_pos = token.position + dice_value
            if projected_pos > 56:
                # Needs exact roll to finish
                return False
            return True
            
        return False

    @staticmethod
    def check_capture(game_state: GameState, moving_token: Token) -> Optional[Token]:
        """
        Checks if the moving token captures any opponent's token.
        Returns the captured token, or None.
        """
        absolute_pos = moving_token.get_absolute_position()
        if absolute_pos == -1 or absolute_pos in SAFE_SQUARES_ABSOLUTE:
            return None

        # Check all other players' tokens
        for color, player in game_state.players.items():
            if color == moving_token.color:
                continue
                
            for token in player.tokens:
                if token.status == TokenStatus.ACTIVE and token.get_absolute_position() == absolute_pos:
                    return token
                    
        return None

    @staticmethod
    def check_win_condition(game_state: GameState, player_color: Color) -> bool:
        """Checks if the given player has all 4 tokens finished."""
        player = game_state.players.get(player_color)
        if not player:
            return False
            
        return all(token.status == TokenStatus.FINISHED for token in player.tokens)
