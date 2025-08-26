import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from dice import Die
from unittest.mock import patch

def test_die_roll():
    die = Die(sides=6)
    for _ in range(100):
        roll = die.roll()
        assert 1 <= roll <= 6

def test_exploding_roll_no_explosion():
    die = Die(sides=6)
    with patch('random.randint', return_value=3) as mock_randint:
        roll = die.exploding_roll()
        assert roll == 3
        mock_randint.assert_called_once_with(1, 6)

def test_exploding_roll_single_explosion():
    die = Die(sides=6)
    with patch('random.randint', side_effect=[6, 3]) as mock_randint:
        roll = die.exploding_roll()
        assert roll == 9 # 6 + 3
        assert mock_randint.call_count == 2

def test_exploding_roll_multiple_explosions():
    die = Die(sides=6)
    with patch('random.randint', side_effect=[6, 6, 4]) as mock_randint:
        roll = die.exploding_roll()
        assert roll == 16 # 6 + 6 + 4
        assert mock_randint.call_count == 3
