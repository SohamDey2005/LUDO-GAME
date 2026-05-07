import pytest
from unittest import mock
from app.models.game import GameState, Color, PlayerType, TokenStatus, GameStatus
from app.services.game_engine import GameEngine
from app.core.rules import RulesEngine
from app.models.config import GameConfig

@pytest.fixture
def initial_game():
    game = GameEngine.create_game()
    GameEngine.add_player(game, "P1", Color.RED, PlayerType.HUMAN)
    GameEngine.add_player(game, "P2", Color.GREEN, PlayerType.HUMAN)
    GameEngine.start_game(game)
    return game

def test_three_consecutive_sixes(initial_game):
    game = initial_game
    game.current_turn = Color.RED
    
    with mock.patch('app.core.dice.Dice.roll', return_value=6):
        game.dice_value = None # Ready to roll
        GameEngine.roll_dice(game) # 1st six
        game.dice_value = None
        GameEngine.roll_dice(game) # 2nd six
        game.dice_value = None
        GameEngine.roll_dice(game) # 3rd six
        
    assert game.consecutive_sixes == 0
    assert game.current_turn == Color.GREEN
    assert "Three consecutive sixes" in game.last_action

def test_stack_blocking(initial_game):
    game = initial_game
    p1 = game.players[Color.RED]
    p2 = game.players[Color.GREEN]
    
    # Red block at absolute position 13 (which is Green's start)
    t1_red = p1.tokens[0]
    t2_red = p1.tokens[1]
    
    t1_red.status = TokenStatus.ACTIVE
    t1_red.position = 13
    
    t2_red.status = TokenStatus.ACTIVE
    t2_red.position = 13
    
    # Green token in base rolling 6
    t1_green = p2.tokens[0]
    game.current_turn = Color.GREEN
    game.dice_value = 6
    
    # Green starting square is 0 for Green's path (absolute 13)
    # RulesEngine.is_valid_move checks destination
    # Entering board puts token at position 0
    assert RulesEngine.is_valid_move(game, t1_green, 6) == False

def test_safe_zone_immunity(initial_game):
    game = initial_game
    p1 = game.players[Color.RED]
    p2 = game.players[Color.GREEN]
    
    # P1 on a safe square (absolute 8)
    t1_red = p1.tokens[0]
    t1_red.status = TokenStatus.ACTIVE
    t1_red.position = 8
    
    # P2 lands on absolute 8
    t1_green = p2.tokens[0]
    t1_green.status = TokenStatus.ACTIVE
    # Green start is 13. Absolute 8 is relative position 47 (13+47=60, 60%52=8)
    t1_green.position = 47
    
    game.current_turn = Color.GREEN
    game.dice_value = 1
    
    GameEngine.move_token(game, t1_green.id)
    
    # Red should NOT be captured because 8 is safe
    assert t1_red.status == TokenStatus.ACTIVE
    assert t1_red.position == 8

def test_exact_roll_to_finish(initial_game):
    game = initial_game
    p1 = game.players[Color.RED]
    t1 = p1.tokens[0]
    
    t1.status = TokenStatus.ACTIVE
    t1.position = 55 # 1 step from finish
    
    # Roll 2
    assert RulesEngine.is_valid_move(game, t1, 2) == False
    # Roll 1
    assert RulesEngine.is_valid_move(game, t1, 1) == True

def test_capture_bonus_turn(initial_game):
    game = initial_game
    p1 = game.players[Color.RED]
    p2 = game.players[Color.GREEN]
    
    # P1 at absolute 10
    t1_red = p1.tokens[0]
    t1_red.status = TokenStatus.ACTIVE
    t1_red.position = 10
    
    # P2 at absolute 9
    t1_green = p2.tokens[0]
    t1_green.status = TokenStatus.ACTIVE
    # Green start 13. Absolute 9 is relative 48.
    t1_green.position = 48
    
    game.current_turn = Color.GREEN
    game.dice_value = 1
    
    GameEngine.move_token(game, t1_green.id)
    
    assert t1_red.status == TokenStatus.BASE
    assert game.current_turn == Color.GREEN # Extra turn
    assert game.dice_value == None
