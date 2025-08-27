import pygame
from ui import Button
from character import Character, SKILLS
from spells import all_spells
from races import all_races
from talents import all_talents
from items import all_items

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

class CharacterCreationScreen:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.attributes = {"warrior": 0, "rogue": 0, "mage": 0}
        self.points = 10
        self.selected_skills = []
        self.selected_race = None
        self.selected_talent = None
        self.is_done = False
        self.character = None

        self.buttons = self._create_buttons()

    def _create_buttons(self):
        buttons = {}

        # Attribute buttons
        for i, attr in enumerate(self.attributes.keys()):
            buttons[f"attr_{attr}_inc"] = Button(200, 100 + i * 50, 40, 40, "+", (0, 255, 0), (0, 0, 0))
            buttons[f"attr_{attr}_dec"] = Button(250, 100 + i * 50, 40, 40, "-", (255, 0, 0), (0, 0, 0))

        # Skill buttons
        y_offset = 0
        for attr, skills in SKILLS.items():
            for skill in skills:
                buttons[f"skill_{skill}"] = Button(320, 100 + y_offset * 40, 150, 30, skill, (100, 100, 100), (255, 255, 255))
                y_offset += 1

        # Race buttons
        for i, race_name in enumerate(all_races.keys()):
            buttons[f"race_{race_name}"] = Button(500, 100 + i * 50, 150, 40, all_races[race_name]["name"], (100, 100, 100), (255, 255, 255))

        # Talent buttons
        y_offset = 0
        for talent_key, talent in all_talents.items():
            if talent.type == "general":
                buttons[f"talent_{talent_key}"] = Button(680, 100 + y_offset * 50, 200, 40, talent.name, (100, 100, 100), (255, 255, 255))
                y_offset += 1

        # Start game button
        buttons["start"] = Button(350, 500, 200, 50, "Start Game", (100, 100, 100), (0, 0, 0))

        return buttons

    def handle_event(self, event):
        for name, button in self.buttons.items():
            if button.is_clicked(event):
                self._handle_button_press(name)

    def _handle_button_press(self, name):
        if name.startswith("attr_"):
            parts = name.split("_")
            attr = parts[1]
            op = parts[2]
            if op == "inc" and self.points > 0 and self.attributes[attr] < 6:
                self.attributes[attr] += 1
                self.points -= 1
            elif op == "dec" and self.attributes[attr] > 0:
                self.attributes[attr] -= 1
                self.points += 1
        elif name.startswith("skill_"):
            skill = name.replace("skill_", "")
            if skill in self.selected_skills:
                self.selected_skills.remove(skill)
            elif len(self.selected_skills) < 3:
                skill_attr = None
                for attr, skills in SKILLS.items():
                    if skill in skills:
                        skill_attr = attr
                        break
                if skill_attr and self.attributes[skill_attr] > 0:
                    self.selected_skills.append(skill)
        elif name.startswith("race_"):
            race_key = name.replace("race_", "")
            self.selected_race = all_races[race_key]
        elif name.startswith("talent_"):
            talent_key = name.replace("talent_", "")
            self.selected_talent = all_talents[talent_key]
        elif name == "start":
            if self.points == 0 and len(self.selected_skills) == 3 and self.selected_race and self.selected_talent:

                final_talents = self.selected_race["talents"] + [self.selected_talent]

                self.character = Character(
                    name="Player",
                    x=10 * 32, y=8 * 32,
                    warrior=self.attributes["warrior"],
                    rogue=self.attributes["rogue"],
                    mage=self.attributes["mage"],
                    skills=self.selected_skills,
                    talents=final_talents
                )

                if self.character.attributes["mage"] > 0:
                    self.character.spellbook.append(all_spells["magic_light"])
                    self.character.spellbook.append(all_spells["healing_hand"])

                # Add starting items
                self.character.inventory.append(all_items["sword"])
                self.character.inventory.append(all_items["leather_armor"])
                self.character.inventory.append(all_items["health_potion"])
                self.character.equip(all_items["sword"])

                if self.character.attributes["mage"] > 0:
                    self.character.inventory.append(all_items["novices_wand"])
                    self.character.equip(all_items["novices_wand"])

                self.is_done = True

    def update(self):
        # Update button colors based on state
        for name, button in self.buttons.items():
            if name.startswith("skill_"):
                skill = name.replace("skill_", "")
                if skill in self.selected_skills:
                    button.color = (0, 200, 0)
                else:
                    button.color = (100, 100, 100)
            elif name.startswith("race_"):
                race_key = name.replace("race_", "")
                if self.selected_race and self.selected_race["name"] == all_races[race_key]["name"]:
                    button.color = (0, 200, 0)
                else:
                    button.color = (100, 100, 100)
            elif name.startswith("talent_"):
                talent_key = name.replace("talent_", "")
                if self.selected_talent and self.selected_talent.name == all_talents[talent_key].name:
                    button.color = (0, 200, 0)
                else:
                    button.color = (100, 100, 100)

        # Enable/disable start button
        if self.points == 0 and len(self.selected_skills) == 3 and self.selected_race and self.selected_talent:
            self.buttons["start"].color = (0, 255, 0)
        else:
            self.buttons["start"].color = (100, 100, 100)

    def draw(self, screen):
        screen.fill((0, 0, 0))
        draw_text(screen, "Character Creation", self.font, (255, 255, 255), 10, 10)
        draw_text(screen, f"Points remaining: {self.points}", self.font, (255, 255, 255), 10, 50)

        # Draw attributes
        for i, (attr, value) in enumerate(self.attributes.items()):
            draw_text(screen, f"{attr.capitalize()}: {value}", self.font, (255, 255, 255), 10, 100 + i * 50)

        # Draw skills
        draw_text(screen, "Skills:", self.font, (255, 255, 255), 320, 50)

        # Draw races
        draw_text(screen, "Race:", self.font, (255, 255, 255), 500, 50)

        # Draw talents
        draw_text(screen, "Talent:", self.font, (255, 255, 255), 680, 50)

        # Draw selected info
        draw_text(screen, f"Selected Race: {self.selected_race['name'] if self.selected_race else 'None'}", self.font, (255, 255, 255), 10, 300)
        draw_text(screen, f"Selected Talent: {self.selected_talent.name if self.selected_talent else 'None'}", self.font, (255, 255, 255), 10, 340)
        draw_text(screen, f"Selected Skills: {', '.join(self.selected_skills)}", self.font, (255, 255, 255), 10, 380)

        # Draw buttons
        for button in self.buttons.values():
            button.draw(screen)
