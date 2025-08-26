import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from character import Character
from spell import Spell
from talents import tough_as_nails, marksman
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

def test_heal():
    char = Character("Test", warrior=5, rogue=2, mage=1)
    char.hp = 1
    char.heal(5)
    assert char.hp == 6
    char.heal(10)
    assert char.hp == 11 # max_hp is 11
    char.heal(1)
    assert char.hp == 11

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

@patch('dice.Die.roll')
def test_cast_spell_success(mock_roll):
    mock_roll.return_value = 5 # Roll a 5, total check is 5 + 3(mage) + 2(thaumaturgy) = 10. DL is 10.
    char = Character("Test", warrior=1, rogue=1, mage=3, skills=["Thaumaturgy"])
    char.mana = 10

    mock_effect = MagicMock()
    spell = Spell("Test Spell", circle=1, dl=10, mana_cost=5, effect=mock_effect)
    char.spellbook.append(spell)

    result = char.cast_spell(spell)

    assert result is True
    assert char.mana == 5
    mock_effect.assert_called_once_with(caster=char, target=None)

@patch('dice.Die.roll')
def test_cast_spell_failure_roll(mock_roll):
    mock_roll.return_value = 1 # Roll a 1, total check is 1 + 3(mage) + 2(thaumaturgy) = 6. DL is 10.
    char = Character("Test", warrior=1, rogue=1, mage=3, skills=["Thaumaturgy"])
    char.mana = 10

    mock_effect = MagicMock()
    spell = Spell("Test Spell", circle=1, dl=10, mana_cost=5, effect=mock_effect)
    char.spellbook.append(spell)

    result = char.cast_spell(spell)

    assert result is False
    assert char.mana == 5 # Mana is consumed even on failure
    mock_effect.assert_not_called()

def test_cast_spell_failure_no_mana():
    char = Character("Test", warrior=1, rogue=1, mage=3, skills=["Thaumaturgy"])
    char.mana = 3

    mock_effect = MagicMock()
    spell = Spell("Test Spell", circle=1, dl=10, mana_cost=5, effect=mock_effect)
    char.spellbook.append(spell)

    result = char.cast_spell(spell)

    assert result is False
    assert char.mana == 3
    mock_effect.assert_not_called()

def test_cast_spell_failure_unknown_spell():
    char = Character("Test", warrior=1, rogue=1, mage=3, skills=["Thaumaturgy"])
    char.mana = 10

    mock_effect = MagicMock()
    spell = Spell("Test Spell", circle=1, dl=10, mana_cost=5, effect=mock_effect)

    result = char.cast_spell(spell)

    assert result is False
    assert char.mana == 10
    mock_effect.assert_not_called()

def test_character_with_talents():
    char = Character("Test", warrior=3, rogue=4, mage=2, talents=[tough_as_nails, marksman])
    # tough_as_nails should increase hp by 2
    assert char.max_hp == 11 # 6 + 3 (warrior) + 2 (talent)
    assert char.hp == 11
    # marksman should give +1 ranged attack bonus
    assert char.ranged_attack_bonus == 1
