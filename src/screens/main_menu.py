import pygame
from ui import Button
from save_manager import save_file_exists

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

class MainMenuScreen:
    def __init__(self):
        self.font = pygame.font.Font(None, 50)
        self.selected_option = None

        self.buttons = self._create_buttons()

    def _create_buttons(self):
        buttons = {}
        buttons["new_game"] = Button(300, 200, 200, 50, "New Game", (0, 200, 0), (255, 255, 255))

        load_game_color = (0, 200, 0) if save_file_exists() else (100, 100, 100)
        buttons["load_game"] = Button(300, 300, 200, 50, "Load Game", load_game_color, (255, 255, 255))

        buttons["quit"] = Button(300, 400, 200, 50, "Quit", (200, 0, 0), (255, 255, 255))
        return buttons

    def handle_event(self, event):
        if self.buttons["new_game"].is_clicked(event):
            self.selected_option = "new_game"
        elif self.buttons["load_game"].is_clicked(event) and save_file_exists():
            self.selected_option = "load_game"
        elif self.buttons["quit"].is_clicked(event):
            self.selected_option = "quit"

    def update(self):
        # The main menu is static, so no update logic is needed for now
        pass

    def draw(self, screen):
        screen.fill((20, 20, 50)) # Dark blue background

        draw_text(screen, "Warrior, Rogue & Mage", self.font, (255, 255, 0), 150, 100)

        # Draw buttons
        for button in self.buttons.values():
            button.draw(screen)
