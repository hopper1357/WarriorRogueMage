class Spell:
    def __init__(self, name, circle, dl, mana_cost, effect):
        self.name = name
        self.circle = circle
        self.dl = dl
        self.mana_cost = mana_cost
        self.effect = effect

    def __str__(self):
        return f"{self.name} (Circle {self.circle})"
