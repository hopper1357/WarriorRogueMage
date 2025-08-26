import random

class Die:
    def __init__(self, sides=6):
        self.sides = sides

    def roll(self):
        return random.randint(1, self.sides)

    def exploding_roll(self):
        total = 0
        while True:
            roll = self.roll()
            total += roll
            if roll != self.sides:
                break
        return total
