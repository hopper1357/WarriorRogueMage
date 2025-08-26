import pygame
from ui import Button
from character import SKILLS
from talents import all_talents
from spells import all_spells
from dice import Die

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

class AdvancementScreen:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.Font(None, 36)
        self.is_done = False
        self.selection_state = "main" # "main", "attribute", "skill", "talent"

        self.buttons = self._create_main_buttons()

    def _create_main_buttons(self):
        buttons = {}
        buttons["attribute"] = Button(300, 150, 200, 50, "Raise Attribute", (0, 200, 0), (255, 255, 255))
        buttons["hp_mana"] = Button(300, 220, 200, 50, "Increase HP/Mana", (0, 200, 0), (255, 255, 255))
        buttons["skill"] = Button(300, 290, 200, 50, "Gain Skill", (0, 200, 0), (255, 255, 255))
        buttons["talent"] = Button(300, 360, 200, 50, "Gain Talent", (0, 200, 0), (255, 255, 255))
        buttons["spell"] = Button(300, 430, 200, 50, "Gain Spell", (0, 200, 0), (255, 255, 255))
        return buttons

    def _create_attribute_buttons(self):
        buttons = {}
        buttons["warrior"] = Button(300, 200, 200, 50, "Warrior +1", (0, 200, 0), (255, 255, 255))
        buttons["rogue"] = Button(300, 270, 200, 50, "Rogue +1", (0, 200, 0), (255, 255, 255))
        buttons["mage"] = Button(300, 340, 200, 50, "Mage +1", (0, 200, 0), (255, 255, 255))
        buttons["back"] = Button(10, 550, 100, 40, "Back", (200, 200, 0), (0, 0, 0))
        return buttons

    def _create_hp_mana_buttons(self):
        buttons = {}
        buttons["hp"] = Button(300, 200, 200, 50, "HP +1d6", (0, 200, 0), (255, 255, 255))
        buttons["mana"] = Button(300, 270, 200, 50, "Mana +1d6", (0, 200, 0), (255, 255, 255))
        buttons["back"] = Button(10, 550, 100, 40, "Back", (200, 200, 0), (0, 0, 0))
        return buttons

    def _create_skill_buttons(self):
        buttons = {}
        y_offset = 0
        for attr, skills in SKILLS.items():
            if self.player.attributes[attr] > 0:
                for skill in skills:
                    if skill not in self.player.skills:
                        buttons[skill] = Button(300, 150 + y_offset * 40, 200, 30, skill, (0, 200, 0), (255, 255, 255))
                        y_offset += 1
        buttons["back"] = Button(10, 550, 100, 40, "Back", (200, 200, 0), (0, 0, 0))
        return buttons

    def _create_talent_buttons(self):
        buttons = {}
        y_offset = 0
        for talent_key, talent in all_talents.items():
            if talent.type == "general" and talent not in self.player.talents:
                buttons[talent_key] = Button(300, 150 + y_offset * 50, 200, 40, talent.name, (0, 200, 0), (255, 255, 255))
                y_offset += 1
        buttons["back"] = Button(10, 550, 100, 40, "Back", (200, 200, 0), (0, 0, 0))
        return buttons

    def _create_spell_buttons(self):
        buttons = {}
        y_offset = 0
        for spell_key, spell in all_spells.items():
            if spell not in self.player.spellbook:
                buttons[spell_key] = Button(300, 150 + y_offset * 50, 200, 40, spell.name, (0, 200, 0), (255, 255, 255))
                y_offset += 1
        buttons["back"] = Button(10, 550, 100, 40, "Back", (200, 200, 0), (0, 0, 0))
        return buttons

    def handle_event(self, event):
        for name, button in self.buttons.items():
            if button.is_clicked(event):
                self._handle_button_press(name)

    def _handle_button_press(self, name):
        if self.selection_state == "main":
            if name == "attribute":
                self.selection_state = "attribute"
                self.buttons = self._create_attribute_buttons()
            elif name == "hp_mana":
                self.selection_state = "hp_mana"
                self.buttons = self._create_hp_mana_buttons()
            elif name == "skill":
                self.selection_state = "skill"
                self.buttons = self._create_skill_buttons()
            elif name == "talent":
                self.selection_state = "talent"
                self.buttons = self._create_talent_buttons()
            elif name == "spell":
                self.selection_state = "spell"
                self.buttons = self._create_spell_buttons()

        elif self.selection_state == "attribute":
            if name in ["warrior", "rogue", "mage"]:
                self.player.attributes[name] += 1
                self.is_done = True
            elif name == "back":
                self.selection_state = "main"
                self.buttons = self._create_main_buttons()

        elif self.selection_state == "skill":
            if name == "back":
                self.selection_state = "main"
                self.buttons = self._create_main_buttons()
            else: # A skill button was clicked
                self.player.skills.append(name)
                self.is_done = True

        elif self.selection_state == "talent":
            if name == "back":
                self.selection_state = "main"
                self.buttons = self._create_main_buttons()
            else: # A talent button was clicked
                talent = all_talents[name]
                self.player.talents.append(talent)
                talent.apply(self.player) # Apply the talent's effect immediately
                self.is_done = True

        elif self.selection_state == "spell":
            if name == "back":
                self.selection_state = "main"
                self.buttons = self._create_main_buttons()
            else: # A spell button was clicked
                spell = all_spells[name]
                self.player.spellbook.append(spell)
                self.is_done = True

        elif self.selection_state == "hp_mana":
            d6 = Die()
            if name == "hp":
                self.player.max_hp += d6.roll()
                self.player.hp = self.player.max_hp
                self.is_done = True
            elif name == "mana":
                self.player.max_mana += d6.roll()
                self.player.mana = self.player.max_mana
                self.is_done = True
            elif name == "back":
                self.selection_state = "main"
                self.buttons = self._create_main_buttons()

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((20, 50, 20)) # Dark green background

        draw_text(screen, "You have Leveled Up!", self.font, (255, 255, 0), 250, 50)
        draw_text(screen, "Choose your advancement:", self.font, (255, 255, 255), 250, 100)

        for button in self.buttons.values():
            button.draw(screen)
