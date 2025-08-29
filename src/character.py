import pygame
from dice import Die
from spell import Spell
from talent import Talent
from items import Weapon, Armor, MagicImplement, Potion
from talents import all_talents
from event_manager import event_manager
import ritual
import quest

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
        self.status_effects = []
        self.inventory = []
        self.journal = []
        self.equipped_weapon = None
        self.equipped_body_armor = None
        self.equipped_shield = None
        self.equipped_hands = None
        self.equipped_implement = None
        self.d6 = Die()
        self.damage_resistances = {}

        # Advancement
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100

        # Bonuses
        self.ranged_attack_bonus = 0
        self.melee_damage_bonus = 0
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
            if item.armor_type == "shield":
                if self.equipped_shield:
                    self.unequip(self.equipped_shield)
                self.equipped_shield = item
            elif item.armor_type == "hands":
                if self.equipped_hands:
                    self.unequip(self.equipped_hands)
                self.equipped_hands = item
            else: # "body"
                if self.equipped_body_armor:
                    self.unequip(self.equipped_body_armor)
                self.equipped_body_armor = item
            print(f"{self.name} equipped {item.name}.")
        elif isinstance(item, MagicImplement):
            if self.equipped_implement:
                self.unequip(self.equipped_implement)
            self.equipped_implement = item
            self.thaumaturgy_bonus += item.thaumaturgy_bonus
            print(f"{self.name} equipped {item.name}.")
        else:
            print(f"{item.name} is not an equippable item.")

        # Apply passive bonuses from the equipped item
        if item.properties.get("melee_damage_bonus"):
            self.melee_damage_bonus += item.properties["melee_damage_bonus"]

    def unequip(self, item):
        if item == self.equipped_weapon:
            self.equipped_weapon = None
            print(f"{self.name} unequipped {item.name}.")
        elif item == self.equipped_body_armor:
            self.equipped_body_armor = None
            print(f"{self.name} unequipped {item.name}.")
        elif item == self.equipped_shield:
            self.equipped_shield = None
            print(f"{self.name} unequipped {item.name}.")
        elif item == self.equipped_hands:
            self.equipped_hands = None
            print(f"{self.name} unequipped {item.name}.")
        elif item == self.equipped_implement:
            self.thaumaturgy_bonus -= item.thaumaturgy_bonus
            self.equipped_implement = None
            print(f"{self.name} unequipped {item.name}.")
        else:
            print(f"{item.name} is not equipped.")

        # Remove passive bonuses from the unequipped item
        if item.properties.get("melee_damage_bonus"):
            self.melee_damage_bonus -= item.properties["melee_damage_bonus"]

    def use_item(self, item):
        if item not in self.inventory:
            print(f"{self.name} does not have {item.name}.")
            return

        if hasattr(item, 'use'):
            item.use(self)
            # Consume the item if it's a potion
            if isinstance(item, Potion):
                self.inventory.remove(item)
                print(f"{self.name} used {item.name}.")
        else:
            print(f"{item.name} is not a usable item.")

    def add_item_to_inventory(self, item):
        self.inventory.append(item)
        event_manager.post({"type": "inventory_updated", "item": item, "character": self})
        print(f"{self.name} received {item.name}.")

    def has_item(self, item_name):
        return any(item.name == item_name for item in self.inventory)

    def remove_item_from_inventory(self, item_name):
        for item in self.inventory:
            if item.name == item_name:
                self.inventory.remove(item)
                print(f"{self.name} lost {item.name}.")
                return True
        return False

    @property
    def total_defense(self):
        bonus = 0
        if self.equipped_body_armor:
            bonus += self.equipped_body_armor.defense_bonus
        if self.equipped_hands:
            bonus += self.equipped_hands.defense_bonus

        # Can't get shield bonus if using a two-handed weapon
        if self.equipped_shield:
            if not (self.equipped_weapon and self.equipped_weapon.two_handed):
                bonus += self.equipped_shield.defense_bonus

        return self.defense + bonus

    @property
    def is_seriously_wounded(self):
        return self.hp <= self.max_hp / 2

    def get_sustained_penalty(self):
        return -len(self.sustained_spells)

    def add_status_effect(self, effect):
        # Prevent duplicate effects of the same name
        if not self.get_status_effect(effect.name):
            self.status_effects.append(effect)
            effect.on_apply(self)
            print(f"{self.name} is now {effect.name}.")

    def get_status_effect(self, effect_name):
        for effect in self.status_effects:
            if effect.name == effect_name:
                return effect
        return None

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

        if self.is_seriously_wounded:
            total -= 3

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

    def take_damage(self, damage, damage_type=None, damage_bonus=0):
        if isinstance(damage, str):
            # Handle dice notation, e.g., "1d6", "2d6-1"
            parts = damage.lower().split('d')
            num_dice = int(parts[0])

            modifier = 0
            if '-' in parts[1]:
                d_parts = parts[1].split('-')
                dice_type = int(d_parts[0])
                modifier = -int(d_parts[1])
            elif '+' in parts[1]:
                d_parts = parts[1].split('+')
                dice_type = int(d_parts[0])
                modifier = int(d_parts[1])
            else:
                dice_type = int(parts[1])

            total_damage = 0
            for _ in range(num_dice):
                # Damage rolls always explode
                total_damage += self.d6.exploding_roll()

            damage = total_damage + modifier

        damage += damage_bonus

        if damage_type and damage_type in self.damage_resistances:
            resistance = self.damage_resistances[damage_type]
            damage = int(damage * (1 - resistance))
            print(f"{self.name} resists {damage_type} damage!")

        final_damage = damage

        self.hp -= final_damage
        if self.hp < 0:
            self.hp = 0

        print(f"{self.name} takes {final_damage} {damage_type or ''} damage.")
        return final_damage

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def restore_mana(self, amount):
        self.mana += amount
        if self.mana > self.max_mana:
            self.mana = self.max_mana

    def spend_fate(self, amount):
        if self.fate >= amount:
            self.fate -= amount
            print(f"{self.name} spends {amount} Fate. Remaining: {self.fate}")
            return True
        print(f"{self.name} does not have enough Fate to spend.")
        return False

    def rest(self):
        """
        Recovers HP and Mana after a day of rest.
        Heals HP equal to the highest attribute.
        Heals an additional 2 HP if the character has the Herbalism skill.
        Fully restores Mana.
        """
        hp_to_recover = max(self.attributes.values())
        if "Herbalism" in self.skills:
            hp_to_recover += 2

        self.heal(hp_to_recover)
        self.mana = self.max_mana
        print(f"{self.name} rests, recovering {hp_to_recover} HP and all Mana.")

    def cast_spell(self, spell, target=None, use_implement=False, enhancement_level=0):
        # Check if the character knows the spell
        if spell not in self.spellbook:
            print(f"{self.name} does not know the spell {spell.name}.")
            return False

        # Calculate final mana cost and DL
        mana_cost = spell.mana_cost
        if self.equipped_body_armor:
            mana_cost += self.equipped_body_armor.armor_penalty
        if self.equipped_shield:
            mana_cost += self.equipped_shield.armor_penalty

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

    def contribute_to_ritual(self, ritual: 'Ritual', mana_amount, from_hp=False):
        if from_hp:
            if all_talents["blood_mage"] not in self.talents:
                print(f"{self.name} is not a Blood Mage and cannot use HP for mana.")
                return False

            # 1 HP = 1 Mana
            if self.hp <= mana_amount: # Can't kill self
                print(f"{self.name} does not have enough HP to contribute {mana_amount} mana.")
                return False

            self.take_damage(mana_amount)
            ritual.pool_mana(self, mana_amount)
            print(f"{self.name} contributes {mana_amount} life force to the ritual.")
            return True
        else:
            if self.mana < mana_amount:
                print(f"{self.name} does not have enough mana to contribute {mana_amount}.")
                return False

            self.mana -= mana_amount
            ritual.pool_mana(self, mana_amount)
            print(f"{self.name} contributes {mana_amount} mana to the ritual.")
            return True

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

    def add_quest(self, quest: 'quest.Quest'):
        if quest not in self.journal:
            self.journal.append(quest)
            print(f"New quest added to journal: {quest.title}")

    def get_quest(self, quest_title):
        for quest in self.journal:
            if quest.title == quest_title:
                return quest
        return None

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
