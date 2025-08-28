from character import Character
from dice import Die
from items import Weapon
from effects import Poisoned

class Combat:
    def __init__(self, char1, char2):
        self.char1 = char1
        self.char2 = char2
        self.d6 = Die()

    def determine_initiative(self):
        char1_roll = self.d6.roll()
        char2_roll = self.d6.roll()

        if char1_roll > char2_roll:
            return self.char1, self.char2
        elif char2_roll > char1_roll:
            return self.char2, self.char1
        else:
            # Reroll on tie
            return self.determine_initiative()

    def attack(self, attacker, defender, weapon):
        if not isinstance(weapon, Weapon):
            raise TypeError("Provided weapon is not a valid Weapon object.")

        # Attack roll
        attack_skill = weapon.skill
        if weapon.type == "ranged":
            attack_attribute = "rogue"
            attack_bonus = attacker.ranged_attack_bonus
        else:
            attack_attribute = "warrior"
            attack_bonus = 0 # No melee bonus for now

        # The DL for the attack is the defender's total defense
        dl = defender.total_defense
        _, total = attacker.attribute_check(attack_attribute, [attack_skill], dl)
        total += attack_bonus
        success = total >= dl

        if success:
            damage_dealt = defender.take_damage(weapon.damage, weapon.damage_type)

            # Special effect for Giant Spider
            if attacker.name == "Giant Spider":
                # 50% chance to poison
                if self.d6.roll() > 3:
                    defender.add_status_effect(Poisoned(duration=3))

            return True, total, damage_dealt
        else:
            return False, total, 0
