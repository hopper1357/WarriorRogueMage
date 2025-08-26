from spell import Spell
from dice import Die

# --- Effect Functions ---

def magic_light_effect(caster, target):
    """Creates a magical light."""
    print(f"A magical light illuminates the area around {caster.name}.")

def healing_hand_effect(caster, target):
    """Heals a target for 1d6 HP."""
    if target is None:
        target = caster

    d6 = Die()
    amount_to_heal = d6.roll()
    target.heal(amount_to_heal)
    print(f"{caster.name}'s healing hand restores {amount_to_heal} HP to {target.name}.")

def frostburn_effect(caster, target):
    """Deals 1d6 damage to a target."""
    if target:
        d6 = Die()
        damage = d6.roll()
        target.take_damage(damage)
        print(f"{caster.name}'s frostburn deals {damage} damage to {target.name}.")

def lightning_bolt_effect(caster, target):
    """Deals 2d6 damage to a target."""
    if target:
        d6 = Die()
        damage = d6.roll() + d6.roll()
        target.take_damage(damage)
        print(f"{caster.name}'s lightning bolt deals {damage} damage to {target.name}.")

# --- Spell Instances ---

# 1st Circle Spells (DL 5, 1 Mana)
magic_light = Spell(
    name="Magic Light",
    circle=1,
    dl=5,
    mana_cost=1,
    effect=magic_light_effect
)

healing_hand = Spell(
    name="Healing Hand",
    circle=1,
    dl=5,
    mana_cost=1,
    effect=healing_hand_effect
)

frostburn = Spell(
    name="Frostburn",
    circle=1,
    dl=5,
    mana_cost=1,
    effect=frostburn_effect
)

# 2nd Circle Spells (DL 7, 3 Mana)
lightning_bolt = Spell(
    name="Lightning Bolt",
    circle=2,
    dl=7,
    mana_cost=3,
    effect=lightning_bolt_effect
)

# A dictionary to easily access all spells
all_spells = {
    "magic_light": magic_light,
    "healing_hand": healing_hand,
    "frostburn": frostburn,
    "lightning_bolt": lightning_bolt,
}
