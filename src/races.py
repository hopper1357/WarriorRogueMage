from talents import all_talents

human = {
    "name": "Human",
    "talents": []
}

elf = {
    "name": "Elf",
    "talents": [
        all_talents["exceptional_attribute_mage"],
        all_talents["sixth_sense"]
    ]
}

dwarf = {
    "name": "Dwarf",
    "talents": [
        all_talents["craftsman"],
        all_talents["no_talent_for_magic"]
    ]
}

# A dictionary to easily access all races
all_races = {
    "human": human,
    "elf": elf,
    "dwarf": dwarf,
}
