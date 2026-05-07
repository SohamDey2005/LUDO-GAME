"""
AI Engine (Rules 17, 23).
AI obeys the EXACT same rule system as human players.
It uses RulesEngine.get_valid_moves() — the same validation path humans use.
No hidden information is accessed. No move is generated outside the validator.
"""
import random
import copy
from app.models.game import GameState, Token, TokenStatus
from app.core.rules import RulesEngine, MoveValidator
from app.ai.heuristics import Evaluator


class AIEngine:

    @staticmethod
    def get_best_move(game_state: GameState, difficulty: str = "medium") -> str | None:
        """
        Returns the token_id of the best move for the current AI player.
        All moves are generated via MoveValidator — same path as human moves.
        """
        # Rule 17: AI uses identical validated move list as humans
        valid_token_ids: list[str] = MoveValidator.get_valid_tokens(
            game_state, game_state.current_turn, game_state.dice_value
        )
        if not valid_token_ids:
            return None

        if difficulty == "easy":
            # Easy: pure random selection from legal moves
            return random.choice(valid_token_ids)

        if difficulty == "medium":
            # Medium: greedy heuristic — pick highest-scoring legal move
            best_score = float('-inf')
            best_id = valid_token_ids[0]
            for token_id in valid_token_ids:
                score = Evaluator.evaluate_move(game_state, token_id, game_state.dice_value)
                if score > best_score:
                    best_score = score
                    best_id = token_id
            return best_id

        if difficulty == "hard":
            # Hard: Expectiminimax depth-1
            # Score = heuristic(our move) − expected_capture_risk(next opponent)
            best_score = float('-inf')
            best_id = valid_token_ids[0]
            player = game_state.players[game_state.current_turn]

            for token_id in valid_token_ids:
                token = next(t for t in player.tokens if t.id == token_id)
                base_score = Evaluator.evaluate_move(game_state, token_id, game_state.dice_value)
                penalty = AIEngine._capture_risk(game_state, token, game_state.dice_value)
                final_score = base_score - penalty
                if final_score > best_score:
                    best_score = final_score
                    best_id = token_id
            return best_id

        return random.choice(valid_token_ids)

    @staticmethod
    def _capture_risk(game_state: GameState, token: Token, dice_value: int) -> float:
        """
        Estimates the probability that the token will be captured on the opponent's
        next turn. Uses the configurable safe zones from game settings.
        """
        # Project token to its new position
        if token.status == TokenStatus.BASE:
            projected_pos = 0
        else:
            projected_pos = token.position + dice_value

        # Create a temporary token at the projected position to get abs position
        sim_token = Token(
            id="sim", color=token.color,
            position=projected_pos, status=TokenStatus.ACTIVE
        )
        sim_abs_pos = sim_token.get_absolute_position()

        # Safe zone → no risk
        if sim_abs_pos == -1 or sim_abs_pos in game_state.settings.safe_zones:
            return 0.0

        capture_risk = 0.0
        for c, player in game_state.players.items():
            if c == token.color:
                continue
            for enemy in player.tokens:
                if enemy.status != TokenStatus.ACTIVE:
                    continue
                enemy_abs = enemy.get_absolute_position()
                if enemy_abs == -1:
                    continue
                # Distance from enemy to our projected position (clockwise)
                dist = (sim_abs_pos - enemy_abs) % 52
                # If enemy is 1-6 squares behind us, they could land on us next roll
                if 1 <= dist <= 6:
                    capture_risk += (1.0 / 6.0) * 100.0  # weighted penalty
        return capture_risk
