from character import Character
from items import all_items
from quests import all_quests
import random

class NPC(Character):
    def __init__(self, name, x, y, warrior, rogue, mage, skills=None, talents=None, dialogue="...", color=(0, 0, 255), quest_to_give=None):
        super().__init__(name, x, y, warrior, rogue, mage, skills, talents, color)
        self.dialogue = dialogue
        self.quest_to_give = quest_to_give

class Monster(Character):
    def __init__(self, name, x, y, warrior, rogue, mage, skills=None, talents=None, color=(0, 255, 0), xp_value=0, loot_table=None):
        super().__init__(name, x, y, warrior, rogue, mage, skills, talents, color)
        self.xp_value = xp_value
        self.loot_table = loot_table if loot_table is not None else []

    def drop_loot(self):
        if self.loot_table:
            return random.choice(self.loot_table)
        return None

class TownGuard(NPC):
    def __init__(self, x, y):
        super().__init__(
            name="Town Guard",
            x=x, y=y,
            warrior=3,
            rogue=2,
            mage=0,
            skills=["Swords", "Awareness"],
            dialogue="There's a goblin lurking nearby. Get rid of it!",
            color=(192, 192, 192), # Silver
            quest_to_give=all_quests["goblin_menace"]
        )

class Goblin(Monster):
    def __init__(self, x, y):
        loot_table = [all_items["dagger"], all_items["health_potion"]]
        super().__init__(
            name="Goblin",
            x=x, y=y,
            warrior=2,
            rogue=3,
            mage=1,
            skills=["Daggers"],
            color=(0, 128, 0), # Dark Green
            xp_value=50,
            loot_table=loot_table
        )

class GiantRat(Monster):
    def __init__(self, x, y):
        super().__init__(
            name="Giant Rat",
            x=x, y=y,
            warrior=1,
            rogue=2,
            mage=0,
            skills=[],
            color=(139, 69, 19), # Brown
            xp_value=10,
            loot_table=[]
        )

class Skeleton(Monster):
    def __init__(self, x, y):
        loot_table = [all_items["sword"]]
        super().__init__(
            name="Skeleton",
            x=x, y=y,
            warrior=3,
            rogue=1,
            mage=0,
            skills=["Swords"],
            color=(255, 255, 255), # White
            xp_value=75,
            loot_table=loot_table
        )
        self.damage_resistances = {"slashing": 0.5, "piercing": 0.5}

class Bandit(Monster):
    def __init__(self, x, y):
        loot_table = [all_items["health_potion"], all_items["sword"]]
        super().__init__(
            name="Bandit",
            x=x, y=y,
            warrior=3,
            rogue=2,
            mage=0,
            skills=["Swords", "Daggers"],
            color=(128, 0, 0), # Maroon
            xp_value=100,
            loot_table=loot_table
        )
        # Equip the bandit
        sword = all_items["sword"]
        leather_armor = all_items["leather_armor"]
        self.inventory.append(sword)
        self.inventory.append(leather_armor)
        self.equip(sword)
        self.equip(leather_armor)

class GiantSpider(Monster):
    def __init__(self, x, y):
        super().__init__(
            name="Giant Spider",
            x=x, y=y,
            warrior=3,
            rogue=4,
            mage=0,
            skills=["Unarmed"],
            color=(50, 50, 50), # Dark Gray
            xp_value=150,
            loot_table=[] # Spiders might not drop items
        )
        bite = all_items["spider_bite"]
        self.inventory.append(bite)
        self.equip(bite)
