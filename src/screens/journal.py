import pygame
from ui import Button

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

class JournalScreen:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        self.is_done = False

        self.buttons = self._create_buttons()

    def _create_buttons(self):
        buttons = {}
        buttons["back"] = Button(650, 500, 100, 50, "Back", (200, 200, 0), (0, 0, 0))
        return buttons

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.is_done = True

        if self.buttons["back"].is_clicked(event):
            self.is_done = True

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((100, 80, 50)) # Brown, book-like background

        draw_text(screen, "Journal", self.font, (255, 255, 255), 10, 10)

        y_offset = 50
        for quest in self.player.journal:
            status = "[COMPLETED]" if quest.is_complete else "[ACTIVE]"
            draw_text(screen, f"{quest.title} {status}", self.font, (255, 255, 0), 20, y_offset)
            y_offset += 40

            draw_text(screen, quest.description, self.small_font, (255, 255, 255), 30, y_offset)
            y_offset += 30

            draw_text(screen, "Objectives:", self.small_font, (255, 255, 255), 30, y_offset)
            y_offset += 25

            for objective in quest.objectives:
                obj_status = "[X]" if objective.is_complete else "[ ]"
                draw_text(screen, f"{obj_status} {objective.description}", self.small_font, (255, 255, 255), 40, y_offset)
                y_offset += 25

            y_offset += 20 # Spacer between quests


        # Draw buttons
        for button in self.buttons.values():
            button.draw(screen)
