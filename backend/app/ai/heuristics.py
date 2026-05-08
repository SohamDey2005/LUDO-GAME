from app.models.game import GameState, Token, Color, TokenStatus
from app.core.rules import RulesEngine, SAFE_SQUARES_ABSOLUTE

class HeuristicWeights:
    CAPTURE_ENEMY = 100
    REACH_FINISH = 200
    REACH_SAFE_ZONE = 50
    ESCAPE_DANGER = 40
    EXPOSE_TOKEN = -60
    CREATE_BLOCK = 70  # Bonus for stacking two tokens together
    ADVANCE_TOWARD_FINISH = 30 # Base value, multiplied by distance

class Evaluator:
    @staticmethod
    def evaluate_move(game_state: GameState, token_id: str, dice_value: int) -> float:
        """
        Evaluates the potential score of moving a specific token.
        Higher score means a better move.
        """
        player = game_state.players[game_state.current_turn]
        token = next((t for t in player.tokens if t.id == token_id), None)
        if not token:
            return -1000

        score = 0
        current_abs_pos = token.get_absolute_position()
        
        # Determine if currently in danger
        was_in_danger = Evaluator.is_in_danger(game_state, token)

        # Simulate move
        projected_pos = token.position + (dice_value if token.status == TokenStatus.ACTIVE else 0)
        if token.status == TokenStatus.BASE:
            projected_pos = 0 # Enters board

        # Advance score (encourage moving tokens closer to finish)
        score += (projected_pos / 56.0) * HeuristicWeights.ADVANCE_TOWARD_FINISH

        if projected_pos == 56:
            score += HeuristicWeights.REACH_FINISH
            return score # Best possible move outcome

        # Create a dummy token for simulated absolute position checking
        sim_token = Token(id="sim", color=token.color, position=projected_pos, status=TokenStatus.ACTIVE)
        sim_abs_pos = sim_token.get_absolute_position()

        # Check Capture
        if sim_abs_pos != -1 and sim_abs_pos not in SAFE_SQUARES_ABSOLUTE:
            # Check if we land on an enemy
            for c, p in game_state.players.items():
                if c != token.color:
                    for t in p.tokens:
                        if t.status == TokenStatus.ACTIVE and t.get_absolute_position() == sim_abs_pos:
                            score += HeuristicWeights.CAPTURE_ENEMY
                            break
                            
        # Check Block Building (landing on own token)
        if sim_abs_pos != -1:
            for t in player.tokens:
                if t.id != token_id and t.status == TokenStatus.ACTIVE:
                    if t.get_absolute_position() == sim_abs_pos:
                        score += HeuristicWeights.CREATE_BLOCK
                        break

        # Check Safe Zone
        if sim_abs_pos in SAFE_SQUARES_ABSOLUTE:
            score += HeuristicWeights.REACH_SAFE_ZONE

        # Danger Evaluation (Look-Ahead)
        risk_score_now = Evaluator.get_danger_score(game_state, sim_token)
        is_in_danger_now = risk_score_now > 0
        
        # Penalize moves based on how much risk they create
        score -= risk_score_now

        if was_in_danger and not is_in_danger_now:
            score += HeuristicWeights.ESCAPE_DANGER
        elif not was_in_danger and is_in_danger_now:
            score += HeuristicWeights.EXPOSE_TOKEN

        return score

    @staticmethod
    def is_in_danger(game_state: GameState, token: Token) -> bool:
        if token.status != TokenStatus.ACTIVE:
            return False
        return Evaluator.is_in_danger_at_pos(game_state, token)

    @staticmethod
    def is_in_danger_at_pos(game_state: GameState, token: Token) -> bool:
        """
        Improved Look-Ahead: Counts how many enemies can reach this position 
        in their next turn. Returns True if at least one enemy can capture.
        """
        abs_pos = token.get_absolute_position()
        if abs_pos == -1 or abs_pos in SAFE_SQUARES_ABSOLUTE:
            return False

        danger_count = 0
        # Check all opponents
        for c, p in game_state.players.items():
            if c != token.color:
                for t in p.tokens:
                    # Enemy must be active to capture
                    if t.status == TokenStatus.ACTIVE:
                        enemy_abs_pos = t.get_absolute_position()
                        if enemy_abs_pos != -1:
                            # Distance from enemy to us on the 52-square perimeter
                            dist = (abs_pos - enemy_abs_pos) % 52
                            # If enemy is within 1-6 squares, we are in danger
                            if 1 <= dist <= 6:
                                danger_count += 1
                                
        return danger_count > 0

    @staticmethod
    def get_danger_score(game_state: GameState, token: Token) -> float:
        """
        Calculates a numeric risk score based on how many enemies threaten this spot.
        Used for deeper 'Look-Ahead' decision making.
        """
        abs_pos = token.get_absolute_position()
        if abs_pos == -1 or abs_pos in SAFE_SQUARES_ABSOLUTE:
            return 0

        risk = 0
        for c, p in game_state.players.items():
            if c != token.color:
                for t in p.tokens:
                    if t.status == TokenStatus.ACTIVE:
                        enemy_abs_pos = t.get_absolute_position()
                        if enemy_abs_pos != -1:
                            dist = (abs_pos - enemy_abs_pos) % 52
                            if 1 <= dist <= 6:
                                # High risk if multiple enemies can reach this spot
                                risk += (7 - dist) * 10 # Closer enemies are more dangerous
        return risk
