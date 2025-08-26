class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return self.name

class Weapon(Item):
    def __init__(self, name, description, damage, skill, weapon_type):
        super().__init__(name, description)
        self.damage = damage
        self.skill = skill
        self.type = weapon_type

class Armor(Item):
    def __init__(self, name, description, defense_bonus, armor_penalty):
        super().__init__(name, description)
        self.defense_bonus = defense_bonus
        self.armor_penalty = armor_penalty

class Potion(Item):
    def __init__(self, name, description, effect):
        super().__init__(name, description)
        self.effect = effect

    def use(self, character):
        self.effect(character)

# --- Item Instances ---

unarmed_strike = Weapon(
    name="Unarmed Strike",
    description="A basic unarmed attack.",
    damage="1d6-3",
    skill="Unarmed",
    weapon_type="melee"
)

def heal_effect(character):
    character.heal(10)

sword = Weapon(
    name="Sword",
    description="A simple sword.",
    damage="1d6",
    skill="Swords",
    weapon_type="melee"
)

leather_armor = Armor(
    name="Leather Armor",
    description="A suit of leather armor.",
    defense_bonus=1,
    armor_penalty=1
)

health_potion = Potion(
    name="Health Potion",
    description="Restores 10 HP.",
    effect=heal_effect
)

# A dictionary to easily access all items
all_items = {
    "unarmed_strike": unarmed_strike,
    "sword": sword,
    "leather_armor": leather_armor,
    "health_potion": health_potion,
}
