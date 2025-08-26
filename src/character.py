from dice import Die
from spell import Spell

SKILLS = {
    "warrior": ["Axes", "Blunt", "Polearms", "Riding", "Swords", "Unarmed"],
    "rogue": ["Acrobatics", "Bows", "Daggers", "Firearms", "Thievery", "Thrown"],
    "mage": ["Alchemy", "Awareness", "Herbalism", "Lore", "Thaumaturgy"],
}

class Character:
    def __init__(self, name, warrior, rogue, mage, skills=None):
        self.name = name
        self.attributes = {
            "warrior": warrior,
            "rogue": rogue,
            "mage": mage,
        }
        self.skills = skills if skills is not None else []
        self.spellbook = []
        self.d6 = Die()

        self.hp = 6 + self.attributes["warrior"]
        self.max_hp = self.hp

        self.fate = max(1, self.attributes["rogue"])

        self.mana = 2 * self.attributes["mage"]
        self.max_mana = self.mana

        self.defense = (self.attributes["warrior"] + self.attributes["rogue"]) // 2 + 4

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

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def cast_spell(self, spell, target=None):
        if spell not in self.spellbook:
            print(f"{self.name} does not know the spell {spell.name}.")
            return False

        if self.mana < spell.mana_cost:
            print(f"{self.name} does not have enough mana to cast {spell.name}.")
            return False

        # Perform a Mage attribute check against the spell's DL
        # The 'Thaumaturgy' skill is relevant for spell casting
        success, total = self.attribute_check("mage", ["Thaumaturgy"], spell.dl)

        if success:
            print(f"{self.name} successfully casts {spell.name} (Total: {total}).")
            self.mana -= spell.mana_cost
            spell.effect(caster=self, target=target)
            return True
        else:
            print(f"{self.name} failed to cast {spell.name} (Total: {total}).")
            # According to WR&M rules, mana is still consumed on a failed casting roll
            self.mana -= spell.mana_cost
            return False

    @property
    def is_dead(self):
        return self.hp <= 0

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
