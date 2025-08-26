import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from character import Character
from unittest.mock import patch, MagicMock

def test_character_initialization():
    char = Character("Test", warrior=3, rogue=4, mage=2, skills=["Swords"])
    assert char.name == "Test"
    assert char.attributes["warrior"] == 3
    assert char.max_hp == 9 # 6 + 3
    assert char.hp == 9
    assert char.max_mana == 4 # 2 * 2
    assert char.mana == 4
    assert char.fate == 4
    assert char.defense == 7 # (3+4)//2 + 4 = 3+4=7

def test_character_initialization_min_fate():
    char = Character("Test", warrior=3, rogue=0, mage=2, skills=["Swords"])
    assert char.fate == 1

def test_take_damage():
    char = Character("Test", warrior=5, rogue=2, mage=1)
    assert char.hp == 11
    char.take_damage(5)
    assert char.hp == 6
    assert not char.is_dead
    char.take_damage(10)
    assert char.hp == 0
    assert char.is_dead

@patch('dice.Die.roll')
def test_attribute_check_success(mock_roll):
    mock_roll.return_value = 5
    char = Character("Test", warrior=4, rogue=2, mage=1, skills=["Swords"])
    # Total = 5 (roll) + 4 (warrior) + 2 (skill bonus) = 11. DL is 10.
    success, total = char.attribute_check("warrior", ["Swords"], 10)
    assert success
    assert total == 11

@patch('dice.Die.roll')
def test_attribute_check_failure(mock_roll):
    mock_roll.return_value = 2
    char = Character("Test", warrior=4, rogue=2, mage=1, skills=["Swords"])
    # Total = 2 (roll) + 4 (warrior) + 2 (skill bonus) = 8. DL is 10.
    success, total = char.attribute_check("warrior", ["Swords"], 10)
    assert not success
    assert total == 8

@patch('dice.Die.roll')
def test_attribute_check_no_skill(mock_roll):
    mock_roll.return_value = 5
    char = Character("Test", warrior=4, rogue=2, mage=1, skills=[])
    # Total = 5 (roll) + 4 (warrior) = 9. DL is 10.
    success, total = char.attribute_check("warrior", ["Swords"], 10)
    assert not success
    assert total == 9

@patch('dice.Die.exploding_roll')
@patch('dice.Die.roll')
def test_attribute_check_exploding_die(mock_roll, mock_exploding_roll):
    mock_roll.return_value = 6
    mock_exploding_roll.return_value = 4 # 6 explodes, new roll is 4
    char = Character("Test", warrior=4, rogue=2, mage=1, skills=["Swords"])
    # Total = 6 (roll) + 4 (exploding) + 4 (warrior) + 2 (skill bonus) = 16. DL is 15.
    success, total = char.attribute_check("warrior", ["Swords"], 15)
    assert success
    assert total == 16

@patch('dice.Die.roll')
def test_opposed_check(mock_roll):
    char1 = Character("Char1", warrior=5, rogue=2, mage=1, skills=["Swords"])
    char2 = Character("Char2", warrior=4, rogue=3, mage=1, skills=[])

    # char1 roll: 5, char2 roll: 3
    mock_roll.side_effect = [5, 3]
    # char1 total: 5(roll) + 5(warrior) + 2(skill) = 12
    # char2 total: 3(roll) + 4(warrior) = 7
    winner, char1_total, char2_total = char1.opposed_check(char2, "warrior", ["Swords"], "warrior", [])
    assert winner == char1
    assert char1_total == 12
    assert char2_total == 7
