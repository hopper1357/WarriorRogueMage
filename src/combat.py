from character import Character
from dice import Die

WEAPONS = {
    "Sword": {"damage": "1d6", "skill": "Swords", "type": "melee"},
    "Dagger": {"damage": "1d6-2", "skill": "Daggers", "type": "melee"},
    "Axe": {"damage": "1d6+1", "skill": "Axes", "type": "melee"},
    "Bow": {"damage": "1d6", "skill": "Bows", "type": "ranged"},
}

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

    def attack(self, attacker, defender, weapon_name):
        if weapon_name not in WEAPONS:
            raise ValueError(f"Unknown weapon: {weapon_name}")

        weapon = WEAPONS[weapon_name]

        # Attack roll
        attack_skill = weapon["skill"]
        if weapon["type"] == "ranged":
            attack_attribute = "rogue"
            attack_bonus = attacker.ranged_attack_bonus
        else:
            attack_attribute = "warrior"
            attack_bonus = 0 # No melee bonus for now

        # The DL for the attack is the defender's defense
        dl = defender.defense
        _, total = attacker.attribute_check(attack_attribute, [attack_skill], dl)
        total += attack_bonus
        success = total >= dl

        if success:
            # Damage roll
            damage_str = weapon["damage"]
            damage_roll = self.d6.exploding_roll() # Damage rolls always explode

            modifier = 0
            if "-" in damage_str:
                modifier = -int(damage_str.split("-")[1])
            elif "+" in damage_str:
                modifier = int(damage_str.split("+")[1])

            damage = damage_roll + modifier
            if damage < 0:
                damage = 0

            defender.take_damage(damage)
            return True, total, damage
        else:
            return False, total, 0
