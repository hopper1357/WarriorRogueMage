class Ritual:
    def __init__(self, spell, primary_caster: 'Character'):
        if spell.duration == 0: # Assuming only non-instantaneous spells can be rituals
            # This is not specified in TASKS.md, but it makes sense.
            # I will assume any spell can be a ritual for now.
            pass

        self.spell = spell
        self.primary_caster = primary_caster
        self.participants = [primary_caster]
        self.total_mana_pooled = 0
        self.time_spent = 0 # in some abstract unit, e.g., hours

    def add_participant(self, character):
        if character not in self.participants:
            self.participants.append(character)

    def pool_mana(self, character, amount):
        if character not in self.participants:
            print(f"{character.name} is not a participant in this ritual.")
            return

        # This logic will be expanded in the Character class method
        self.total_mana_pooled += amount

    def spend_time(self, hours):
        self.time_spent += hours

    def perform_ritual(self, target=None):
        if self.total_mana_pooled < self.spell.mana_cost:
            print("Not enough mana has been pooled to perform the ritual.")
            return False

        # DL reduction based on time spent. 1 hour = -1 DL.
        dl_reduction = self.time_spent
        final_dl = self.spell.dl - dl_reduction

        # The primary caster makes the roll
        success, total = self.primary_caster.attribute_check("mage", ["Thaumaturgy"], final_dl)

        if success:
            print(f"The ritual to cast {self.spell.name} was a success! (Total: {total})")
            self.spell.effect(caster=self.primary_caster, target=target, enhancement_level=0)
            return True
        else:
            print(f"The ritual to cast {self.spell.name} failed. (Total: {total})")
            return False

    def __str__(self):
        return f"Ritual for {self.spell.name} led by {self.primary_caster.name}"
