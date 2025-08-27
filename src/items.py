from spells import all_spells

class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return self.name

class Weapon(Item):
    def __init__(self, name, description, damage, skill, weapon_type, damage_type="blunt"):
        super().__init__(name, description)
        self.damage = damage
        self.skill = skill
        self.type = weapon_type
        self.damage_type = damage_type

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

class MagicImplement(Item):
    def __init__(self, name, description, level, thaumaturgy_bonus, stored_spells=None):
        super().__init__(name, description)
        self.level = level
        self.thaumaturgy_bonus = thaumaturgy_bonus
        self.stored_spells = stored_spells if stored_spells is not None else []
        self.max_mana = 10 * self.level
        self.mana_pool = self.max_mana

# --- Item Instances ---

unarmed_strike = Weapon(
    name="Unarmed Strike",
    description="A basic unarmed attack.",
    damage="1d6-3",
    skill="Unarmed",
    weapon_type="melee",
    damage_type="blunt"
)

def heal_effect(character):
    character.heal(10)

def restore_mana_effect(character):
    character.restore_mana(10)

sword = Weapon(
    name="Sword",
    description="A simple sword.",
    damage="1d6",
    skill="Swords",
    weapon_type="melee",
    damage_type="slashing"
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

dagger = Weapon(
    name="Dagger",
    description="A small dagger.",
    damage="1d6-2",
    skill="Daggers",
    weapon_type="melee",
    damage_type="piercing"
)

chain_mail = Armor(
    name="Chain Mail",
    description="A suit of chain mail.",
    defense_bonus=3,
    armor_penalty=2
)

mana_potion = Potion(
    name="Mana Potion",
    description="Restores 10 Mana.",
    effect=restore_mana_effect
)

novices_wand = MagicImplement(
    name="Novice's Wand",
    description="A simple wand for a starting mage.",
    level=1,
    thaumaturgy_bonus=1,
    stored_spells=[all_spells["magic_light"]]
)

# A dictionary to easily access all items
all_items = {
    "unarmed_strike": unarmed_strike,
    "sword": sword,
    "dagger": dagger,
    "leather_armor": leather_armor,
    "chain_mail": chain_mail,
    "health_potion": health_potion,
    "mana_potion": mana_potion,
    "novices_wand": novices_wand,
}
