import pytest
from app.models.game import Color, PlayerType, TokenStatus, GameStatus
from app.services.game_engine import GameEngine
from app.core.rules import RulesEngine

def test_create_and_start_game():
    game = GameEngine.create_game()
    assert game.status == GameStatus.WAITING
    
    player_red = GameEngine.add_player(game, "Alice", Color.RED, PlayerType.HUMAN)
    player_blue = GameEngine.add_player(game, "Bob", Color.BLUE, PlayerType.AI)
    
    assert len(game.players) == 2
    assert len(player_red.tokens) == 4
    
    GameEngine.start_game(game)
    assert game.status == GameStatus.IN_PROGRESS
    assert game.current_turn == Color.RED  # Red is first in turn_order

def test_roll_dice_and_move():
    game = GameEngine.create_game()
    GameEngine.add_player(game, "Alice", Color.RED, PlayerType.HUMAN)
    GameEngine.add_player(game, "Bob", Color.BLUE, PlayerType.AI)
    GameEngine.start_game(game)
    
    # Mock dice roll to 6
    game.dice_value = 6
    token_id = game.players[Color.RED].tokens[0].id
    
    GameEngine.move_token(game, token_id)
    token = game.players[Color.RED].tokens[0]
    
    assert token.status == TokenStatus.ACTIVE
    assert token.position == 0
    assert game.current_turn == Color.RED  # Extra turn on 6
    assert game.dice_value is None

def test_capture_token():
    game = GameEngine.create_game()
    red = GameEngine.add_player(game, "Alice", Color.RED, PlayerType.HUMAN)
    blue = GameEngine.add_player(game, "Bob", Color.BLUE, PlayerType.AI)
    GameEngine.start_game(game)
    
    # Put Red token at absolute pos 10
    red_token = red.tokens[0]
    red_token.status = TokenStatus.ACTIVE
    red_token.position = 10
    
    # Put Blue token at relative 23 -> (23 + 39) % 52 = 62 % 52 = 10 (absolute pos 10)
    blue_token = blue.tokens[0]
    blue_token.status = TokenStatus.ACTIVE
    blue_token.position = 23
    
    assert red_token.get_absolute_position() == blue_token.get_absolute_position()
    assert red_token.get_absolute_position() not in {0, 8, 13, 21, 26, 34, 39, 47} # Not a safe square
    
    # Let Red roll a 1 from pos 9 (so it lands on 10)
    red_token.position = 9
    game.dice_value = 1
    
    GameEngine.move_token(game, red_token.id)
    
    assert red_token.position == 10
    assert blue_token.status == TokenStatus.BASE
    assert blue_token.position == -1
    
    # Red gets an extra turn on capture
    assert game.current_turn == Color.RED
    assert game.dice_value is None
