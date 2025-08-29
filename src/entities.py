from character import Character
from items import all_items
from quests import all_quests
import random

class NPC(Character):
    def __init__(self, name, x, y, warrior, rogue, mage, skills=None, talents=None, dialogue="...", color=(0, 0, 255)):
        super().__init__(name, x, y, warrior, rogue, mage, skills, talents, color)
        self.dialogue = dialogue

    def interact(self, player):
        """Default interaction is to just return the dialogue."""
        return self.dialogue

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
            dialogue="Seen any trouble?",
            color=(192, 192, 192) # Silver
        )
        self.heirloom_quest_complete = False

    def interact(self, player):
        heirloom_quest = player.get_quest("The Stolen Heirloom")

        if self.heirloom_quest_complete:
            return "Thank you again for recovering the heirloom."

        if not heirloom_quest:
            # Give the quest
            player.add_quest(all_quests["stolen_heirloom"])
            return "A bandit leader stole my family's heirloom! Please, get it back."

        if heirloom_quest.is_complete:
            if player.has_item("Stolen Heirloom"):
                player.remove_item_from_inventory("Stolen Heirloom")
                heirloom_quest.give_reward(player)
                self.heirloom_quest_complete = True
                return "You found it! Thank you! Here is your reward."
            else:
                # This case shouldn't happen if quest is complete, but good to handle
                return "The quest is done, but you don't have the heirloom..."
        else:
            return "Still searching for that heirloom? The bandit leader must have it."

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
        loot_table = [
            all_items["health_potion"],
            all_items["sword"],
            all_items["two_handed_sword"],
            all_items["rune_blade"]
        ]
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

class BanditLeader(Bandit):
    def __init__(self, x, y):
        # Call the parent's __init__ but we will override some values
        super().__init__(x, y)

        self.name = "Bandit Leader"
        self.attributes["warrior"] = 4
        self.attributes["rogue"] = 3
        self.xp_value = 250
        self.color = (255, 0, 0) # Red to stand out
        self.image.fill(self.color)

        # The Bandit Leader always drops the heirloom
        self.loot_table = [all_items["stolen_heirloom"]]

        # Give him better gear than a standard bandit
        self.unequip(all_items["leather_armor"])
        chain_mail = all_items["chain_mail"]
        self.inventory.append(chain_mail)
        self.equip(chain_mail)

class Drake(Monster):
    def __init__(self, x, y):
        super().__init__(
            name="Drake",
            x=x, y=y,
            warrior=5,
            rogue=3,
            mage=2,
            skills=["Unarmed"],
            color=(139, 0, 0), # Dark Red
            xp_value=300,
            loot_table=[all_items["gauntlets_of_strength"]]
        )
        # Drakes fight with their claws/bite, modeled as unarmed
        unarmed = all_items["unarmed_strike"]
        self.inventory.append(unarmed)
        self.equip(unarmed)
