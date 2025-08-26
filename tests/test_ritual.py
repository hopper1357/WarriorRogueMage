import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from character import Character
from spell import Spell
from ritual import Ritual
from talents import blood_mage
from unittest.mock import patch, MagicMock

@patch('dice.Die.roll')
def test_ritual_success(mock_roll):
    mock_roll.return_value = 10 # High roll to ensure success

    caster1 = Character("Caster1", x=0, y=0, warrior=1, rogue=1, mage=5, skills=["Thaumaturgy"])
    caster2 = Character("Caster2", x=0, y=0, warrior=1, rogue=1, mage=4)
    caster1.mana = 50
    caster2.mana = 50

    mock_effect = MagicMock()
    # High cost, high DL spell
    ritual_spell = Spell("Great Summoning", 4, 15, 60, mock_effect)

    ritual = Ritual(spell=ritual_spell, primary_caster=caster1)
    ritual.add_participant(caster2)

    # Pool mana
    caster1.contribute_to_ritual(ritual, 30)
    caster2.contribute_to_ritual(ritual, 30)
    assert ritual.total_mana_pooled == 60

    # Spend time to reduce DL
    ritual.spend_time(2) # DL becomes 15 - 2 = 13

    # Perform ritual
    # Check: 10(roll) + 5(mage) + 2(skill) = 17. 17 >= 13 is True.
    result = ritual.perform_ritual()

    assert result is True
    mock_effect.assert_called_once()

@patch('dice.Die.roll')
def test_ritual_failure_not_enough_mana(mock_roll):
    mock_roll.return_value = 10
    caster1 = Character("Caster1", x=0, y=0, warrior=1, rogue=1, mage=5)

    ritual_spell = Spell("Great Summoning", 4, 15, 60, lambda c,t,e: None)
    ritual = Ritual(spell=ritual_spell, primary_caster=caster1)

    caster1.contribute_to_ritual(ritual, 30)

    result = ritual.perform_ritual()
    assert result is False

@patch('dice.Die.roll')
def test_ritual_failure_bad_roll(mock_roll):
    mock_roll.return_value = 2 # Low roll
    caster1 = Character("Caster1", x=0, y=0, warrior=1, rogue=1, mage=5, skills=["Thaumaturgy"])
    caster1.mana = 60

    ritual_spell = Spell("Great Summoning", 4, 15, 60, lambda c,t,e: None)
    ritual = Ritual(spell=ritual_spell, primary_caster=caster1)

    caster1.contribute_to_ritual(ritual, 60)

    # Check: 2(roll) + 5(mage) + 2(skill) = 9. 9 >= 15 is False.
    result = ritual.perform_ritual()
    assert result is False

def test_ritual_with_blood_mage():
    caster1 = Character("Caster1", x=0, y=0, warrior=1, rogue=1, mage=5)
    caster1.hp = 50
    caster2 = Character("Blood Mage", x=0, y=0, warrior=1, rogue=1, mage=4, talents=[blood_mage])
    caster2.hp = 50

    ritual_spell = Spell("Great Summoning", 4, 15, 60, lambda c,t,e: None)
    ritual = Ritual(spell=ritual_spell, primary_caster=caster1)
    ritual.add_participant(caster2)

    # Pool mana using HP
    caster2.contribute_to_ritual(ritual, 20, from_hp=True)

    assert ritual.total_mana_pooled == 20
    assert caster2.hp == 30
