from character import Character

class NPC(Character):
    def __init__(self, name, x, y, warrior, rogue, mage, skills=None, talents=None, dialogue="...", color=(0, 0, 255)):
        super().__init__(name, x, y, warrior, rogue, mage, skills, talents, color)
        self.dialogue = dialogue

class Monster(Character):
    def __init__(self, name, x, y, warrior, rogue, mage, skills=None, talents=None, color=(0, 255, 0)):
        super().__init__(name, x, y, warrior, rogue, mage, skills, talents, color)
        # Monsters can have specific AI behaviors in the future
        pass

class TownGuard(NPC):
    def __init__(self, x, y):
        super().__init__(
            name="Town Guard",
            x=x, y=y,
            warrior=3,
            rogue=2,
            mage=0,
            skills=["Swords", "Awareness"],
            dialogue="Move along, citizen.",
            color=(192, 192, 192) # Silver
        )

class Goblin(Monster):
    def __init__(self, x, y):
        super().__init__(
            name="Goblin",
            x=x, y=y,
            warrior=2,
            rogue=3,
            mage=1,
            skills=["Daggers"],
            color=(0, 128, 0) # Dark Green
        )
