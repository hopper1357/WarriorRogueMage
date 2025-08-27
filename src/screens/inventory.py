import pygame
from ui import Button
from items import Weapon, Armor, Potion, MagicImplement

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

class InventoryScreen:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.Font(None, 36)
        self.is_done = False

        self.buttons = self._create_buttons()

    def _create_buttons(self):
        buttons = {}
        # Create buttons for each item in the inventory
        for i, item in enumerate(self.player.inventory):
            if isinstance(item, (Weapon, Armor, MagicImplement)):
                buttons[f"equip_{i}"] = Button(500, 100 + i * 50, 100, 40, "Equip", (0, 200, 0), (255, 255, 255))
            elif isinstance(item, Potion):
                buttons[f"use_{i}"] = Button(500, 100 + i * 50, 100, 40, "Use", (0, 100, 200), (255, 255, 255))

        buttons["back"] = Button(650, 500, 100, 50, "Back", (200, 200, 0), (0, 0, 0))
        return buttons

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.is_done = True

        for name, button in self.buttons.items():
            if button.is_clicked(event):
                if name == "back":
                    self.is_done = True
                elif name.startswith("equip_"):
                    item_index = int(name.split("_")[1])
                    item_to_equip = self.player.inventory[item_index]
                    self.player.equip(item_to_equip)
                    # Recreate buttons to reflect changes
                    self.buttons = self._create_buttons()
                elif name.startswith("use_"):
                    item_index = int(name.split("_")[1])
                    # Ensure the index is still valid after potential list modifications
                    if item_index < len(self.player.inventory):
                        item_to_use = self.player.inventory[item_index]
                        self.player.use_item(item_to_use)
                        # Recreate buttons to reflect the new inventory state
                        self.buttons = self._create_buttons()

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((50, 50, 100)) # Dark blue background

        draw_text(screen, "Inventory", self.font, (255, 255, 255), 10, 10)

        # Draw inventory items
        draw_text(screen, "Items:", self.font, (255, 255, 255), 10, 50)
        for i, item in enumerate(self.player.inventory):
            draw_text(screen, item.name, self.font, (255, 255, 255), 10, 100 + i * 50)

        # Draw equipped items
        draw_text(screen, "Equipped:", self.font, (255, 255, 255), 300, 50)
        weapon_name = self.player.equipped_weapon.name if self.player.equipped_weapon else "None"
        armor_name = self.player.equipped_armor.name if self.player.equipped_armor else "None"
        implement_name = self.player.equipped_implement.name if self.player.equipped_implement else "None"
        draw_text(screen, f"Weapon: {weapon_name}", self.font, (255, 255, 255), 300, 100)
        draw_text(screen, f"Armor: {armor_name}", self.font, (255, 255, 255), 300, 150)
        draw_text(screen, f"Implement: {implement_name}", self.font, (255, 255, 255), 300, 200)
        if self.player.equipped_implement:
            draw_text(screen, f"  Mana: {self.player.equipped_implement.mana_pool}/{self.player.equipped_implement.max_mana}", self.font, (255, 255, 255), 300, 230)


        # Draw buttons
        for button in self.buttons.values():
            button.draw(screen)
