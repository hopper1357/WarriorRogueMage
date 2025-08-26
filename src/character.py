import pygame
from dice import Die
from spell import Spell
from talent import Talent
from items import Weapon, Armor, MagicImplement

SKILLS = {
    "warrior": ["Axes", "Blunt", "Polearms", "Riding", "Swords", "Unarmed"],
    "rogue": ["Acrobatics", "Bows", "Daggers", "Firearms", "Thievery", "Thrown"],
    "mage": ["Alchemy", "Awareness", "Herbalism", "Lore", "Thaumaturgy"],
}

class Character(pygame.sprite.Sprite):
    def __init__(self, name, x, y, warrior, rogue, mage, skills=None, talents=None, color=(255, 0, 0)):
        super().__init__()
        self.name = name

        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.attributes = {
            "warrior": warrior,
            "rogue": rogue,
            "mage": mage,
        }
        self.skills = skills if skills is not None else []
        self.talents = talents if talents is not None else []
        self.spellbook = []
        self.sustained_spells = []
        self.inventory = []
        self.equipped_weapon = None
        self.equipped_armor = None
        self.equipped_implement = None
        self.d6 = Die()
        self.damage_resistances = {}

        # Advancement
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100

        # Bonuses
        self.ranged_attack_bonus = 0
        self.awareness_bonus = 0
        self.lore_bonus = 0
        self.thaumaturgy_bonus = 0

        self.hp = 6 + self.attributes["warrior"]
        self.max_hp = self.hp

        self.fate = max(1, self.attributes["rogue"])

        self.mana = 2 * self.attributes["mage"]
        self.max_mana = self.mana

        self.defense = (self.attributes["warrior"] + self.attributes["rogue"]) // 2 + 4

        self.apply_talents()

    def apply_talents(self):
        for talent in self.talents:
            talent.apply(self)

    def equip(self, item):
        if item not in self.inventory:
            print(f"{self.name} does not have {item.name} in their inventory.")
            return

        if isinstance(item, Weapon):
            if self.equipped_weapon:
                self.unequip(self.equipped_weapon)
            self.equipped_weapon = item
            print(f"{self.name} equipped {item.name}.")
        elif isinstance(item, Armor):
            if self.equipped_armor:
                self.unequip(self.equipped_armor)
            self.equipped_armor = item
            print(f"{self.name} equipped {item.name}.")
        elif isinstance(item, MagicImplement):
            if self.equipped_implement:
                self.unequip(self.equipped_implement)
            self.equipped_implement = item
            self.thaumaturgy_bonus += item.thaumaturgy_bonus
            print(f"{self.name} equipped {item.name}.")
        else:
            print(f"{item.name} is not an equippable item.")

    def unequip(self, item):
        if item == self.equipped_weapon:
            self.equipped_weapon = None
            print(f"{self.name} unequipped {item.name}.")
        elif item == self.equipped_armor:
            self.equipped_armor = None
            print(f"{self.name} unequipped {item.name}.")
        elif item == self.equipped_implement:
            self.thaumaturgy_bonus -= item.thaumaturgy_bonus
            self.equipped_implement = None
            print(f"{self.name} unequipped {item.name}.")
        else:
            print(f"{item.name} is not equipped.")

    @property
    def total_defense(self):
        bonus = self.equipped_armor.defense_bonus if self.equipped_armor else 0
        return self.defense + bonus

    def get_sustained_penalty(self):
        return -len(self.sustained_spells)

    def _get_attribute_check_total(self, attribute, relevant_skills):
        if attribute not in self.attributes:
            raise ValueError(f"Invalid attribute: {attribute}")

        roll = self.d6.roll()
        attribute_value = self.attributes[attribute]

        has_skill = any(skill in self.skills for skill in relevant_skills)

        skill_bonus = 0
        if has_skill:
            skill_bonus = 2

        if has_skill and roll == 6:
            roll += self.d6.exploding_roll()

        total = roll + attribute_value + skill_bonus

        # Apply talent bonuses for specific skills
        if "Awareness" in relevant_skills:
            total += self.awareness_bonus
        if "Lore" in relevant_skills:
            total += self.lore_bonus
        if "Thaumaturgy" in relevant_skills:
            total += self.thaumaturgy_bonus

        total += self.get_sustained_penalty()

        return total

    def attribute_check(self, attribute, relevant_skills, dl):
        total = self._get_attribute_check_total(attribute, relevant_skills)
        return total >= dl, total

    def opposed_check(self, opponent, self_attribute, self_skills, opponent_attribute, opponent_skills):
        self_total = self._get_attribute_check_total(self_attribute, self_skills)
        opponent_total = opponent._get_attribute_check_total(opponent_attribute, opponent_skills)

        if self_total > opponent_total:
            return self, self_total, opponent_total
        elif opponent_total > self_total:
            return opponent, self_total, opponent_total
        else:
            return None, self_total, opponent_total # Tie

    def take_damage(self, damage, damage_type=None):
        if damage_type and damage_type in self.damage_resistances:
            resistance = self.damage_resistances[damage_type]
            damage = int(damage * (1 - resistance))
            print(f"{self.name} resists {damage_type} damage!")

        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def cast_spell(self, spell, target=None, use_implement=False, enhancement_level=0):
        # Check if the character knows the spell
        if spell not in self.spellbook:
            print(f"{self.name} does not know the spell {spell.name}.")
            return False

        # Calculate final mana cost and DL
        mana_cost = spell.mana_cost
        if self.equipped_armor:
            mana_cost += self.equipped_armor.armor_penalty

        enhancement_cost = enhancement_level * (spell.mana_cost // 2)
        mana_cost += enhancement_cost

        dl = spell.dl + enhancement_level

        # Determine which mana pool to use
        source_name = self.name
        can_use_implement = use_implement and self.equipped_implement and spell in self.equipped_implement.stored_spells

        if can_use_implement:
            source_name = self.equipped_implement.name
            if self.equipped_implement.mana_pool < mana_cost:
                print(f"{source_name} does not have enough mana.")
                return False
        else:
            if self.mana < mana_cost:
                print(f"{self.name} does not have enough mana.")
                return False

        # Perform a Mage attribute check against the spell's DL
        success, total = self.attribute_check("mage", ["Thaumaturgy"], dl)

        if success:
            print(f"{self.name} successfully casts {spell.name} from {source_name} (Total: {total}).")
            if can_use_implement:
                self.equipped_implement.mana_pool -= mana_cost
            else:
                self.mana -= mana_cost

            if spell.duration > 0 and spell not in self.sustained_spells:
                self.sustained_spells.append(spell)

            spell.effect(caster=self, target=target, enhancement_level=enhancement_level)
            return True
        else:
            print(f"{self.name} failed to cast {spell.name} from {source_name} (Total: {total}).")
            if use_implement and implement_knows_spell:
                self.equipped_implement.mana_pool -= mana_cost
            else:
                self.mana -= mana_cost
            return False

    @property
    def is_dead(self):
        return self.hp <= 0

    def add_xp(self, amount):
        self.xp += amount
        leveled_up = False
        while self.xp >= self.xp_to_next_level:
            self.level += 1
            self.xp -= self.xp_to_next_level
            self.xp_to_next_level = int(self.xp_to_next_level * 1.5) # Increase xp requirement for next level
            leveled_up = True
            print(f"{self.name} has reached level {self.level}!")
        return leveled_up

    def __str__(self):
        return (
            f"Name: {self.name}\\n"
            f"Attributes: {self.attributes}\\n"
            f"Skills: {self.skills}\\n"
            f"HP: {self.hp}/{self.max_hp}\\n"
            f"Mana: {self.mana}/{self.max_mana}\\n"
            f"Fate: {self.fate}\\n"
            f"Defense: {self.defense}"
        )
