import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from combat import Combat
from character import Character
from items import all_items
from unittest.mock import patch

def test_rune_blade_ignores_armor():
    """
    Tests that a weapon with the 'ignores_armor' property targets the defender's
    base defense instead of their total defense.
    """
    # Attacker has low stats, but the Rune Blade
    attacker = Character("Attacker", x=0, y=0, warrior=1, rogue=1, mage=1, skills=["Swords"])
    rune_blade = all_items["rune_blade"]
    attacker.inventory.append(rune_blade)
    attacker.equip(rune_blade)

    # Defender has high armor
    defender = Character("Defender", x=0, y=0, warrior=1, rogue=1, mage=1)
    plate_armor = all_items["plate_armor"]
    defender.inventory.append(plate_armor)
    defender.equip(plate_armor)

    # Defender's base defense is 4 + (1+1)//2 = 5
    # Defender's total defense with Plate Armor is 5 + 4 = 9
    assert defender.defense == 5
    assert defender.total_defense == 9

    combat = Combat(attacker, defender)

    # We mock the dice roll to control the outcome.
    # Attacker's check: roll + warrior(1) + skill(2) = roll + 3
    # If armor is NOT ignored, DL is 9. Attacker needs a 6 to hit.
    # If armor IS ignored, DL is 5. Attacker needs a 2 to hit.

    # We will make the roll a 3. This should fail against armor, but succeed without it.
    with patch.object(attacker.d6, 'roll', return_value=3):
        # Attack roll total will be 3 (roll) + 1 (warrior) + 2 (skill) = 6
        # This is > 5 (base defense) but < 9 (total defense)
        success, total, damage = combat.attack(attacker, defender, rune_blade)

        assert success is True, "The Rune Blade attack should have ignored armor and succeeded."
