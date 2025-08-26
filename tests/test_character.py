import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from character import Character
from spell import Spell
from talents import tough_as_nails, marksman, alertness, scholar
from items import Weapon, Armor, MagicImplement
from unittest.mock import patch, MagicMock

def test_character_initialization():
    char = Character("Test", x=0, y=0, warrior=3, rogue=4, mage=2, skills=["Swords"])
    assert char.name == "Test"
    assert char.attributes["warrior"] == 3
    assert char.max_hp == 9 # 6 + 3
    assert char.hp == 9
    assert char.max_mana == 4 # 2 * 2
    assert char.mana == 4
    assert char.fate == 4
    assert char.defense == 7 # (3+4)//2 + 4 = 3+4=7

def test_character_initialization_min_fate():
    char = Character("Test", x=0, y=0, warrior=3, rogue=0, mage=2, skills=["Swords"])
    assert char.fate == 1

def test_take_damage():
    char = Character("Test", x=0, y=0, warrior=5, rogue=2, mage=1)
    assert char.hp == 11
    char.take_damage(5)
    assert char.hp == 6
    assert not char.is_dead
    char.take_damage(10)
    assert char.hp == 0
    assert char.is_dead

def test_heal():
    char = Character("Test", x=0, y=0, warrior=5, rogue=2, mage=1)
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
    char = Character("Test", x=0, y=0, warrior=4, rogue=2, mage=1, skills=["Swords"])
    # Total = 5 (roll) + 4 (warrior) + 2 (skill bonus) = 11. DL is 10.
    success, total = char.attribute_check("warrior", ["Swords"], 10)
    assert success
    assert total == 11

@patch('dice.Die.roll')
def test_attribute_check_failure(mock_roll):
    mock_roll.return_value = 2
    char = Character("Test", x=0, y=0, warrior=4, rogue=2, mage=1, skills=["Swords"])
    # Total = 2 (roll) + 4 (warrior) + 2 (skill bonus) = 8. DL is 10.
    success, total = char.attribute_check("warrior", ["Swords"], 10)
    assert not success
    assert total == 8

@patch('dice.Die.roll')
def test_attribute_check_no_skill(mock_roll):
    mock_roll.return_value = 5
    char = Character("Test", x=0, y=0, warrior=4, rogue=2, mage=1, skills=[])
    # Total = 5 (roll) + 4 (warrior) = 9. DL is 10.
    success, total = char.attribute_check("warrior", ["Swords"], 10)
    assert not success
    assert total == 9

@patch('dice.Die.exploding_roll')
@patch('dice.Die.roll')
def test_attribute_check_exploding_die(mock_roll, mock_exploding_roll):
    mock_roll.return_value = 6
    mock_exploding_roll.return_value = 4 # 6 explodes, new roll is 4
    char = Character("Test", x=0, y=0, warrior=4, rogue=2, mage=1, skills=["Swords"])
    # Total = 6 (roll) + 4 (exploding) + 4 (warrior) + 2 (skill bonus) = 16. DL is 15.
    success, total = char.attribute_check("warrior", ["Swords"], 15)
    assert success
    assert total == 16

@patch('dice.Die.roll')
def test_opposed_check(mock_roll):
    char1 = Character("Char1", x=0, y=0, warrior=5, rogue=2, mage=1, skills=["Swords"])
    char2 = Character("Char2", x=0, y=0, warrior=4, rogue=3, mage=1, skills=[])

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
    char = Character("Test", x=0, y=0, warrior=1, rogue=1, mage=3, skills=["Thaumaturgy"])
    char.mana = 10

    mock_effect = MagicMock()
    spell = Spell("Test Spell", circle=1, dl=10, mana_cost=5, effect=mock_effect)
    char.spellbook.append(spell)

    result = char.cast_spell(spell)

    assert result is True
    assert char.mana == 5
    mock_effect.assert_called_once_with(caster=char, target=None, enhancement_level=0)

@patch('dice.Die.roll')
def test_cast_spell_failure_roll(mock_roll):
    mock_roll.return_value = 1 # Roll a 1, total check is 1 + 3(mage) + 2(thaumaturgy) = 6. DL is 10.
    char = Character("Test", x=0, y=0, warrior=1, rogue=1, mage=3, skills=["Thaumaturgy"])
    char.mana = 10

    mock_effect = MagicMock()
    spell = Spell("Test Spell", circle=1, dl=10, mana_cost=5, effect=mock_effect)
    char.spellbook.append(spell)

    result = char.cast_spell(spell)

    assert result is False
    assert char.mana == 5 # Mana is consumed even on failure
    mock_effect.assert_not_called()

def test_cast_spell_failure_no_mana():
    char = Character("Test", x=0, y=0, warrior=1, rogue=1, mage=3, skills=["Thaumaturgy"])
    char.mana = 3

    mock_effect = MagicMock()
    spell = Spell("Test Spell", circle=1, dl=10, mana_cost=5, effect=mock_effect)
    char.spellbook.append(spell)

    result = char.cast_spell(spell)

    assert result is False
    assert char.mana == 3
    mock_effect.assert_not_called()

def test_cast_spell_failure_unknown_spell():
    char = Character("Test", x=0, y=0, warrior=1, rogue=1, mage=3, skills=["Thaumaturgy"])
    char.mana = 10

    mock_effect = MagicMock()
    spell = Spell("Test Spell", circle=1, dl=10, mana_cost=5, effect=mock_effect)

    result = char.cast_spell(spell)

    assert result is False
    assert char.mana == 10
    mock_effect.assert_not_called()

def test_character_with_talents():
    char = Character("Test", x=0, y=0, warrior=3, rogue=4, mage=2, talents=[tough_as_nails, marksman])
    # tough_as_nails should increase hp by 2
    assert char.max_hp == 11 # 6 + 3 (warrior) + 2 (talent)
    assert char.hp == 11
    # marksman should give +1 ranged attack bonus
    assert char.ranged_attack_bonus == 1

def test_equipment():
    char = Character("Test", x=0, y=0, warrior=3, rogue=2, mage=3)
    assert char.total_defense == 6 # (3+2)//2 + 4 = 6

    leather_armor = Armor("Leather Armor", "Some leather armor", defense_bonus=1, armor_penalty=1)
    char.inventory.append(leather_armor)
    char.equip(leather_armor)

    assert char.equipped_armor == leather_armor
    assert char.total_defense == 7 # 6 + 1

    char.unequip(leather_armor)
    assert char.equipped_armor is None
    assert char.total_defense == 6

@patch('dice.Die.roll')
def test_cast_spell_with_armor_penalty(mock_roll):
    mock_roll.return_value = 5 # Success roll
    char = Character("Test", x=0, y=0, warrior=1, rogue=1, mage=3, skills=["Thaumaturgy"])
    char.mana = 10

    mock_effect = MagicMock()
    spell = Spell("Test Spell", circle=1, dl=10, mana_cost=5, effect=mock_effect)
    char.spellbook.append(spell)

    leather_armor = Armor("Leather Armor", "Some leather armor", defense_bonus=1, armor_penalty=1)
    char.inventory.append(leather_armor)
    char.equip(leather_armor)

    result = char.cast_spell(spell)

    assert result is True
    assert char.mana == 4 # 10 - (5 + 1)
    mock_effect.assert_called_once_with(caster=char, target=None, enhancement_level=0)

def test_add_xp_and_level_up():
    char = Character("Test", x=0, y=0, warrior=1, rogue=1, mage=1)
    assert char.level == 1
    assert char.xp == 0
    assert char.xp_to_next_level == 100

    leveled_up = char.add_xp(50)
    assert not leveled_up
    assert char.xp == 50

    leveled_up = char.add_xp(60)
    assert leveled_up
    assert char.level == 2
    assert char.xp == 10 # 110 - 100
    assert char.xp_to_next_level == 150 # 100 * 1.5

@patch('dice.Die.roll')
def test_talent_bonus_attribute_check(mock_roll):
    mock_roll.return_value = 5
    char = Character("Test", x=0, y=0, warrior=1, rogue=1, mage=3, skills=["Awareness"], talents=[alertness])
    # Total = 5 (roll) + 3 (mage) + 2 (skill) + 1 (talent) = 11
    success, total = char.attribute_check("mage", ["Awareness"], 11)
    assert success
    assert total == 11

def test_damage_resistance():
    char = Character("Test", x=0, y=0, warrior=5, rogue=2, mage=1)
    char.damage_resistances = {"slashing": 0.5}
    char.hp = 11

    char.take_damage(10, "slashing")
    assert char.hp == 6 # 11 - (10 * 0.5)

    char.take_damage(4, "blunt")
    assert char.hp == 2 # No resistance

@patch('dice.Die.roll')
def test_magic_implement_bonus(mock_roll):
    mock_roll.return_value = 5
    char = Character("Test", x=0, y=0, warrior=1, rogue=1, mage=3, skills=["Thaumaturgy"])

    implement = MagicImplement("Test Wand", "A wand for testing", level=1, thaumaturgy_bonus=2)
    char.inventory.append(implement)
    char.equip(implement)

    # Total = 5 (roll) + 3 (mage) + 2 (skill) + 2 (implement) = 12
    success, total = char.attribute_check("mage", ["Thaumaturgy"], 12)
    assert success
    assert total == 12

    char.unequip(implement)
    # Total = 5 (roll) + 3 (mage) + 2 (skill) = 10
    success, total = char.attribute_check("mage", ["Thaumaturgy"], 10)
    assert success
    assert total == 10

@patch('dice.Die.roll')
def test_cast_enhanced_spell(mock_roll):
    mock_roll.return_value = 10 # Success roll
    char = Character("Test", x=0, y=0, warrior=1, rogue=1, mage=4, skills=["Thaumaturgy"])
    char.mana = 20

    mock_effect = MagicMock()
    # Base cost: 4 mana, DL 8
    spell = Spell("Test Spell", circle=1, dl=8, mana_cost=4, effect=mock_effect)
    char.spellbook.append(spell)

    # Enhance twice:
    # Mana cost = 4 (base) + 2 * (4/2) = 8
    # DL = 8 + 2 = 10
    # Attribute check: 10(roll) + 4(mage) + 2(skill) = 16. 16 >= 10 is True.
    result = char.cast_spell(spell, enhancement_level=2)

    assert result is True
    assert char.mana == 12 # 20 - 8
    mock_effect.assert_called_once_with(caster=char, target=None, enhancement_level=2)

@patch('dice.Die.roll')
def test_cast_spell_from_implement(mock_roll):
    mock_roll.return_value = 5 # Success roll
    char = Character("Test", x=0, y=0, warrior=1, rogue=1, mage=3, skills=["Thaumaturgy"])
    char.mana = 20

    mock_effect = MagicMock()
    spell = Spell("Test Spell", circle=1, dl=10, mana_cost=5, effect=mock_effect)
    char.spellbook.append(spell)

    implement = MagicImplement("Test Wand", "A wand for testing", level=1, thaumaturgy_bonus=0, stored_spells=[spell])
    implement.mana_pool = 10
    char.inventory.append(implement)
    char.equip(implement)

    # Cast from implement
    result = char.cast_spell(spell, use_implement=True)
    assert result is True
    assert char.mana == 20 # Character mana should not be used
    assert implement.mana_pool == 5 # Implement mana should be used
    mock_effect.assert_called_with(caster=char, target=None, enhancement_level=0)
    assert mock_effect.call_count == 1

    # Cast from implement again, should succeed
    result = char.cast_spell(spell, use_implement=True)
    assert result is True
    assert implement.mana_pool == 0 # Implement mana should be used

    # Try to cast from implement again, should fail
    result = char.cast_spell(spell, use_implement=True)
    assert result is False # Not enough mana
    assert implement.mana_pool == 0 # Should not change

    # Cast from self (not using implement flag)
    result = char.cast_spell(spell, use_implement=False)
    assert result is True
    assert char.mana == 15 # Character mana should be used
    assert mock_effect.call_count == 3
    mock_effect.assert_called_with(caster=char, target=None, enhancement_level=0)

@patch('dice.Die.roll')
def test_sustained_spell_penalty(mock_roll):
    mock_roll.return_value = 5
    char = Character("Test", x=0, y=0, warrior=1, rogue=1, mage=3, skills=["Thaumaturgy"])

    sustained_spell = Spell("Sustained Spell", circle=1, dl=10, mana_cost=5, effect=lambda c,t,e: None, duration=10)
    char.sustained_spells.append(sustained_spell)

    # Total = 5 (roll) + 3 (mage) + 2 (skill) - 1 (penalty) = 9
    success, total = char.attribute_check("mage", ["Thaumaturgy"], 10)
    assert not success
    assert total == 9

    char.sustained_spells.pop()
    # Total = 5 (roll) + 3 (mage) + 2 (skill) = 10
    success, total = char.attribute_check("mage", ["Thaumaturgy"], 10)
    assert success
    assert total == 10
