class StatusEffect:
    """
    Base class for status effects.
    """
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration
        self.owner = None

    def on_apply(self, owner):
        """Called when the effect is first applied."""
        self.owner = owner

    def on_turn_start(self):
        """Called at the beginning of the owner's turn."""
        pass

    def on_remove(self):
        """Called when the effect is removed (e.g., duration expires)."""
        pass

    def __str__(self):
        return f"{self.name} ({self.duration} turns left)"


class Poisoned(StatusEffect):
    """
    Deals damage to the owner at the start of their turn.
    """
    def __init__(self, duration, damage=2):
        super().__init__("Poisoned", duration)
        self.damage = damage

    def on_turn_start(self):
        if self.owner:
            print(f"{self.owner.name} takes {self.damage} damage from poison.")
            self.owner.take_damage(self.damage, 'poison')
