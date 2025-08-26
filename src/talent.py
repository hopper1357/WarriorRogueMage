class Talent:
    def __init__(self, name, description, effect, talent_type="general"):
        self.name = name
        self.description = description
        self.effect = effect
        self.type = talent_type

    def apply(self, character):
        self.effect(character)

    def __str__(self):
        return self.name
