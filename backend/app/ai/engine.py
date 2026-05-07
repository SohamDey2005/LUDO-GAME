import random
from app.models.game import GameState, Token
from app.core.rules import RulesEngine
from app.ai.heuristics import Evaluator

class AIEngine:
    @staticmethod
    def get_best_move(game_state: GameState, difficulty: str = "medium") -> str:
        """
        Returns the token_id of the best move for the current player.
        """
        valid_tokens = RulesEngine.get_valid_moves(game_state, game_state.current_turn, game_state.dice_value)
        if not valid_tokens:
            return None

        if difficulty == "easy":
            return random.choice(valid_tokens).id

        if difficulty == "medium":
            # Heuristic greedy approach
            best_score = float('-inf')
            best_token = None
            for token in valid_tokens:
                score = Evaluator.evaluate_move(game_state, token.id, game_state.dice_value)
                if score > best_score:
                    best_score = score
                    best_token = token
            return best_token.id

        if difficulty == "hard":
            # Expectiminimax depth 1 (evaluate our move + average worst case of next player)
            # For simplicity and performance, we'll use a deeper heuristic that penalizes moves 
            # that put us in paths heavily trafficked by opponents.
            best_score = float('-inf')
            best_token = None
            for token in valid_tokens:
                base_score = Evaluator.evaluate_move(game_state, token.id, game_state.dice_value)
                
                # Expectiminimax penalty: check probability of being captured in the next turn
                # by simulating all 6 dice rolls for the *next* player in turn order.
                penalty = AIEngine._calculate_risk_penalty(game_state, token, game_state.dice_value)
                
                final_score = base_score - penalty
                
                if final_score > best_score:
                    best_score = final_score
                    best_token = token
            return best_token.id

        return random.choice(valid_tokens).id

    @staticmethod
    def _calculate_risk_penalty(game_state: GameState, token: Token, dice_value: int) -> float:
        """Calculates expected risk penalty by checking all 6 possible rolls of opponents."""
        # Simulate our position
        projected_pos = token.position + (dice_value if token.status == 'active' else 0)
        if token.status == 'base': projected_pos = 0
        
        sim_token = Token(id="sim", color=token.color, position=projected_pos, status='active')
        sim_abs_pos = sim_token.get_absolute_position()
        
        if sim_abs_pos == -1 or sim_abs_pos in [0, 8, 13, 21, 26, 34, 39, 47]:
            return 0 # Safe
            
        capture_risk = 0
        # Check all enemies
        for c, p in game_state.players.items():
            if c != token.color:
                for enemy_token in p.tokens:
                    if enemy_token.status == 'active':
                        enemy_pos = enemy_token.get_absolute_position()
                        if enemy_pos != -1:
                            dist = (sim_abs_pos - enemy_pos) % 52
                            # If enemy is 1-6 squares behind, they have a 1/6 chance of rolling exact number
                            if 1 <= dist <= 6:
                                capture_risk += (1.0 / 6.0) * 100 # 100 penalty weight
        return capture_risk
