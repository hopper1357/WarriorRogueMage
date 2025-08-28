import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from character import Character
from spell import Spell
from talents import tough_as_nails, marksman, alertness, scholar, blood_mage
from items import Weapon, Armor, MagicImplement, all_items
from effects import Poisoned
from ritual import Ritual
from quest import Quest
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

def test_seriously_wounded_status():
    char = Character("Test", x=0, y=0, warrior=4, rogue=2, mage=1) # max_hp is 10
    assert not char.is_seriously_wounded

    char.hp = 6
    assert not char.is_seriously_wounded

    char.hp = 5
    assert char.is_seriously_wounded

    char.hp = 2
    assert char.is_seriously_wounded

    char.hp = 0
    assert char.is_seriously_wounded

    char.heal(6) # hp is 6
    assert not char.is_seriously_wounded

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

def test_poisoned_status_effect():
    char = Character("Test", x=0, y=0, warrior=5, rogue=1, mage=1) # max_hp=11
    initial_hp = char.hp

    poison_effect = Poisoned(duration=3, damage=2)
    char.add_status_effect(poison_effect)

    assert len(char.status_effects) == 1
    assert char.get_status_effect("Poisoned") is not None

    # Simulate turn 1
    poison_effect.on_turn_start()
    assert char.hp == initial_hp - 2

    # Simulate turn 2
    poison_effect.on_turn_start()
    assert char.hp == initial_hp - 4

    # Simulate turn 3
    poison_effect.on_turn_start()
    assert char.hp == initial_hp - 6

    # After duration, the effect should be removed by the combat loop,
    # but we can test the state here.
    assert poison_effect.duration == 3 # Duration doesn't change on the effect itself

def test_spend_fate():
    char = Character("Test", x=0, y=0, warrior=1, rogue=3, mage=1) # fate = 3

    # Case 1: Spend fate successfully
    assert char.fate == 3
    result = char.spend_fate(1)
    assert result is True
    assert char.fate == 2

    # Case 2: Spend more fate than available
    result = char.spend_fate(3) # Only has 2 left
    assert result is False
    assert char.fate == 2 # Fate should not change

    # Case 3: Spend remaining fate
    result = char.spend_fate(2)
    assert result is True
    assert char.fate == 0

    # Case 4: Spend fate when at zero
    result = char.spend_fate(1)
    assert result is False
    assert char.fate == 0

def test_use_mana_potion():
    char = Character("Test", x=0, y=0, warrior=1, rogue=1, mage=5) # max_mana = 10
    mana_potion = all_items["mana_potion"]

    # Case 1: Restore mana from 0
    char.mana = 0
    char.inventory.append(mana_potion)
    assert mana_potion in char.inventory

    char.use_item(mana_potion)

    assert char.mana == 10
    assert mana_potion not in char.inventory

    # Case 2: Should not exceed max mana
    char.mana = 5
    char.inventory.append(mana_potion)

    char.use_item(mana_potion)

    assert char.mana == 10 # Not 15
    assert mana_potion not in char.inventory

def test_rest_mechanic():
    # Test case 1: Standard rest
    char = Character("Test", x=0, y=0, warrior=4, rogue=3, mage=2) # max_hp=10, max_mana=4, highest_attr=4
    char.hp = 1
    char.mana = 0

    char.rest()

    assert char.hp == 5 # 1 + 4
    assert char.mana == 4 # max_mana

    # Test case 2: Rest with Herbalism skill
    char_herbalist = Character("Herbalist", x=0, y=0, warrior=2, rogue=3, mage=5, skills=["Herbalism"]) # max_hp=8, max_mana=10, highest_attr=5
    char_herbalist.hp = 1
    char_herbalist.mana = 0

    char_herbalist.rest()

    assert char_herbalist.hp == 8 # 1 + 5 (mage) + 2 (herbalism)
    assert char_herbalist.mana == 10 # max_mana

    # Test case 3: Rest should not exceed max HP
    char.hp = char.max_hp - 1 # hp is 9
    char.rest()
    assert char.hp == char.max_hp # Should be 10, not 13

@patch('dice.Die.roll')
def test_seriously_wounded_penalty(mock_roll):
    mock_roll.return_value = 5
    char = Character("Test", x=0, y=0, warrior=4, rogue=2, mage=1, skills=["Swords"])
    char.hp = 5 # max_hp is 10, so this is exactly half
    assert char.is_seriously_wounded

    # Total = 5 (roll) + 4 (warrior) + 2 (skill) - 3 (penalty) = 8
    success, total = char.attribute_check("warrior", ["Swords"], 10)
    assert not success
    assert total == 8

    char.heal(1) # hp is now 6, not seriously wounded
    assert not char.is_seriously_wounded
    # Total = 5 (roll) + 4 (warrior) + 2 (skill) = 11
    success, total = char.attribute_check("warrior", ["Swords"], 10)
    assert success
    assert total == 11

def test_journal():
    char = Character("Test", x=0, y=0, warrior=1, rogue=1, mage=1)
    assert len(char.journal) == 0

    quest = Quest("Test Quest", "A quest for testing.", [], lambda p: None)
    char.add_quest(quest)

    assert len(char.journal) == 1
    assert char.get_quest("Test Quest") == quest
    assert char.get_quest("Non-existent Quest") is None

def test_contribute_to_ritual():
    char = Character("Test", x=0, y=0, warrior=1, rogue=1, mage=3)
    char.mana = 20
    char.hp = 20

    spell = Spell("Ritual Spell", 4, 13, 50, lambda c,t,e: None)
    ritual = Ritual(spell, char)

    # Contribute mana normally
    result = char.contribute_to_ritual(ritual, 10)
    assert result is True
    assert char.mana == 10
    assert ritual.total_mana_pooled == 10

    # Try to contribute with HP without talent
    result = char.contribute_to_ritual(ritual, 5, from_hp=True)
    assert result is False
    assert char.hp == 20
    assert ritual.total_mana_pooled == 10

    # Give talent and contribute with HP
    char.talents.append(blood_mage)
    result = char.contribute_to_ritual(ritual, 5, from_hp=True)
    assert result is True
    assert char.hp == 15
    assert ritual.total_mana_pooled == 15

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
