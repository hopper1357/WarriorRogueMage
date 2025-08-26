import pygame
from character import Character

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

class GameplayScreen:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.Font(None, 36)

        # Simple player representation for now
        self.player_rect = pygame.Rect(400, 300, 40, 40)
        self.player_speed = 5

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                if len(self.player.spellbook) > 0:
                    self.player.cast_spell(self.player.spellbook[0])
            if event.key == pygame.K_2:
                if len(self.player.spellbook) > 1:
                    self.player.cast_spell(self.player.spellbook[1])
            # Add more keys for more spells if needed

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_rect.x -= self.player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_rect.x += self.player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player_rect.y -= self.player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player_rect.y += self.player_speed

        # Keep player on screen
        if self.player_rect.left < 0:
            self.player_rect.left = 0
        if self.player_rect.right > 800:
            self.player_rect.right = 800
        if self.player_rect.top < 0:
            self.player_rect.top = 0
        if self.player_rect.bottom > 600:
            self.player_rect.bottom = 600

    def draw(self, screen):
        screen.fill((25, 100, 25)) # A green background for the world

        # Draw player
        pygame.draw.rect(screen, (255, 0, 0), self.player_rect) # Red square for the player

        # Draw HUD
        self._draw_hud(screen)

    def _draw_hud(self, screen):
        # Simple HUD on the bottom of the screen
        hud_rect = pygame.Rect(0, 500, 800, 100)
        pygame.draw.rect(screen, (50, 50, 50), hud_rect)

        draw_text(screen, f"HP: {self.player.hp}/{self.player.max_hp}", self.font, (255, 255, 255), 10, 510)
        draw_text(screen, f"Mana: {self.player.mana}/{self.player.max_mana}", self.font, (255, 255, 255), 10, 550)
        draw_text(screen, f"Fate: {self.player.fate}", self.font, (255, 255, 255), 200, 510)
        draw_text(screen, f"Defense: {self.player.defense}", self.font, (255, 255, 255), 200, 550)

        # Display spells
        draw_text(screen, "Spells:", self.font, (255, 255, 255), 400, 510)
        for i, spell in enumerate(self.player.spellbook):
            draw_text(screen, f"({i+1}) {spell.name}", self.font, (255, 255, 255), 400, 550 + i * 40)
