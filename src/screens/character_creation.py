import pygame
from ui import Button
from character import Character, SKILLS
from spells import all_spells

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
        self.is_done = False
        self.character = None

        self.buttons = self._create_buttons()

    def _create_buttons(self):
        buttons = {}

        # Attribute buttons
        for i, attr in enumerate(self.attributes.keys()):
            buttons[f"{attr}_inc"] = Button(200, 100 + i * 50, 40, 40, "+", (0, 255, 0), (0, 0, 0))
            buttons[f"{attr}_dec"] = Button(250, 100 + i * 50, 40, 40, "-", (255, 0, 0), (0, 0, 0))

        # Skill buttons
        y_offset = 0
        for attr, skills in SKILLS.items():
            for skill in skills:
                buttons[skill] = Button(400, 100 + y_offset * 40, 150, 30, skill, (100, 100, 100), (255, 255, 255))
                y_offset += 1

        # Start game button
        buttons["start"] = Button(300, 500, 200, 50, "Start Game", (0, 255, 0), (0, 0, 0))

        return buttons

    def handle_event(self, event):
        for name, button in self.buttons.items():
            if button.is_clicked(event):
                self._handle_button_press(name)

    def _handle_button_press(self, name):
        if name.endswith("_inc"):
            attr = name.split("_")[0]
            if self.points > 0 and self.attributes[attr] < 6:
                self.attributes[attr] += 1
                self.points -= 1
        elif name.endswith("_dec"):
            attr = name.split("_")[0]
            if self.attributes[attr] > 0:
                self.attributes[attr] -= 1
                self.points += 1
        elif name == "start":
            if self.points == 0 and len(self.selected_skills) == 3:
                self.character = Character("Player", self.attributes["warrior"], self.attributes["rogue"], self.attributes["mage"], self.selected_skills)
                if self.character.attributes["mage"] > 0:
                    self.character.spellbook.append(all_spells["magic_light"])
                    self.character.spellbook.append(all_spells["healing_hand"])
                self.is_done = True
        else: # Skill button
            skill = name
            if skill in self.selected_skills:
                self.selected_skills.remove(skill)
            elif len(self.selected_skills) < 3:
                # Check if the character has points in the required attribute
                skill_attr = None
                for attr, skills in SKILLS.items():
                    if skill in skills:
                        skill_attr = attr
                        break
                if skill_attr and self.attributes[skill_attr] > 0:
                    self.selected_skills.append(skill)

    def update(self):
        # Update button colors based on state
        for skill, button in self.buttons.items():
            if skill in SKILLS["warrior"] or skill in SKILLS["rogue"] or skill in SKILLS["mage"]:
                if skill in self.selected_skills:
                    button.color = (0, 200, 0) # Green
                else:
                    button.color = (100, 100, 100) # Gray

        # Enable/disable start button
        if self.points == 0 and len(self.selected_skills) == 3:
            self.buttons["start"].color = (0, 255, 0) # Green
        else:
            self.buttons["start"].color = (100, 100, 100) # Gray

    def draw(self, screen):
        screen.fill((0, 0, 0))
        draw_text(screen, "Character Creation", self.font, (255, 255, 255), 10, 10)
        draw_text(screen, f"Points remaining: {self.points}", self.font, (255, 255, 255), 10, 50)

        # Draw attributes
        for i, (attr, value) in enumerate(self.attributes.items()):
            draw_text(screen, f"{attr.capitalize()}: {value}", self.font, (255, 255, 255), 10, 100 + i * 50)

        # Draw skills
        draw_text(screen, "Selected Skills:", self.font, (255, 255, 255), 10, 300)
        for i, skill in enumerate(self.selected_skills):
            draw_text(screen, skill, self.font, (255, 255, 255), 10, 340 + i * 40)

        # Draw buttons
        for button in self.buttons.values():
            button.draw(screen)
