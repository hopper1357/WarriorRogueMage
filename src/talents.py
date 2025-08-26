from talent import Talent

# --- Effect Functions ---

def tough_as_nails_effect(character):
    """Increases character's max HP by 2."""
    character.max_hp += 2
    character.hp += 2

def marksman_effect(character):
    """Increases character's ranged attack bonus by 1."""
    if not hasattr(character, 'ranged_attack_bonus'):
        character.ranged_attack_bonus = 0
    character.ranged_attack_bonus += 1

def exceptional_attribute_mage_effect(character):
    """Increases character's Mage attribute by 1."""
    character.attributes["mage"] += 1

def sixth_sense_effect(character):
    """Increases character's awareness bonus by 1."""
    if not hasattr(character, 'awareness_bonus'):
        character.awareness_bonus = 0
    character.awareness_bonus += 1

def craftsman_effect(character):
    """Provides a bonus to crafting-related skills (no effect yet)."""
    pass

def no_talent_for_magic_effect(character):
    """Character cannot use magic."""
    character.attributes["mage"] = 0
    character.max_mana = 0
    character.mana = 0

def alertness_effect(character):
    """Increases character's awareness bonus by 1."""
    if not hasattr(character, 'awareness_bonus'):
        character.awareness_bonus = 0
    character.awareness_bonus += 1

def scholar_effect(character):
    """Increases character's lore bonus by 1."""
    if not hasattr(character, 'lore_bonus'):
        character.lore_bonus = 0
    character.lore_bonus += 1

def blood_mage_effect(character):
    """Allows sacrificing HP for Mana in rituals."""
    pass

# --- Talent Instances ---

tough_as_nails = Talent(
    name="Tough as Nails",
    description="+2 Hit Points.",
    effect=tough_as_nails_effect
)

marksman = Talent(
    name="Marksman",
    description="+1 to all ranged attack rolls.",
    effect=marksman_effect
)

exceptional_attribute_mage = Talent(
    name="Exceptional Attribute (Mage)",
    description="+1 to Mage attribute.",
    effect=exceptional_attribute_mage_effect,
    talent_type="racial"
)

sixth_sense = Talent(
    name="Sixth Sense",
    description="+1 to Awareness checks.",
    effect=sixth_sense_effect,
    talent_type="racial"
)

craftsman = Talent(
    name="Craftsman",
    description="Bonus to crafting-related skills.",
    effect=craftsman_effect,
    talent_type="racial"
)

no_talent_for_magic = Talent(
    name="No Talent for Magic",
    description="Cannot use magic.",
    effect=no_talent_for_magic_effect,
    talent_type="racial"
)

alertness = Talent(
    name="Alertness",
    description="+1 to Awareness checks.",
    effect=alertness_effect
)

scholar = Talent(
    name="Scholar",
    description="+1 to Lore checks.",
    effect=scholar_effect
)

blood_mage = Talent(
    name="Blood Mage",
    description="May sacrifice HP for Mana in rituals.",
    effect=blood_mage_effect
)

# A dictionary to easily access all talents
all_talents = {
    "tough_as_nails": tough_as_nails,
    "marksman": marksman,
    "exceptional_attribute_mage": exceptional_attribute_mage,
    "sixth_sense": sixth_sense,
    "craftsman": craftsman,
    "no_talent_for_magic": no_talent_for_magic,
    "alertness": alertness,
    "scholar": scholar,
    "blood_mage": blood_mage,
}
