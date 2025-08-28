import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from entities import Bandit
from items import all_items

def test_bandit_initialization():
    """
    Tests that the Bandit is created with the correct stats, skills, and equipment.
    """
    bandit = Bandit(x=0, y=0)

    assert bandit.name == "Bandit"
    assert bandit.attributes["warrior"] == 3
    assert bandit.attributes["rogue"] == 2
    assert bandit.attributes["mage"] == 0
    assert "Swords" in bandit.skills
    assert "Daggers" in bandit.skills
    assert bandit.xp_value == 100

    # Check for equipped items
    assert bandit.equipped_weapon is not None
    assert bandit.equipped_weapon.name == "Sword"
    assert bandit.equipped_armor is not None
    assert bandit.equipped_armor.name == "Leather Armor"

    # Check that the items are also in the main inventory list
    assert all_items["sword"] in bandit.inventory
    assert all_items["leather_armor"] in bandit.inventory
