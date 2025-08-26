import pygame
from character import Character
from entities import TownGuard, Goblin
from save_manager import save_game

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

class GameplayScreen:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.Font(None, 36)

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)

        self.npcs = pygame.sprite.Group()
        guard = TownGuard(x=100, y=100)
        self.all_sprites.add(guard)
        self.npcs.add(guard)

        self.monsters = pygame.sprite.Group()
        goblin = Goblin(x=600, y=400)
        self.all_sprites.add(goblin)
        self.monsters.add(goblin)

        self.player_speed = 5
        self.dialogue_to_show = None
        self.active_monster = None
        self.save_message_timer = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                if len(self.player.spellbook) > 0:
                    self.player.cast_spell(self.player.spellbook[0])
            elif event.key == pygame.K_2:
                if len(self.player.spellbook) > 1:
                    self.player.cast_spell(self.player.spellbook[1])
            elif event.key == pygame.K_i:
                from main import GameState
                return GameState.INVENTORY
            elif event.key == pygame.K_F5:
                save_game(self.player)
                self.save_message_timer = 120 # Show message for 120 frames (2 seconds)
        from main import GameState
        return GameState.GAMEPLAY

    def update(self, screen):
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.rect.x -= self.player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.rect.x += self.player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.rect.y -= self.player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.rect.y += self.player_speed

        # Keep player on screen
        self.player.rect.clamp_ip(screen.get_rect())

        # Update save message timer
        if self.save_message_timer > 0:
            self.save_message_timer -= 1

        # Interaction logic
        self.dialogue_to_show = None
        for npc in self.npcs:
            if self.player.rect.colliderect(npc.rect.inflate(20, 20))):
                self.dialogue_to_show = npc.dialogue
                break # Show one dialogue at a time

        for monster in self.monsters:
            if self.player.rect.colliderect(monster.rect.inflate(20, 20))):
                self.active_monster = monster
                from main import GameState
                return GameState.COMBAT, self.active_monster

        from main import GameState
        return GameState.GAMEPLAY, None

    def draw(self, screen):
        screen.fill((25, 100, 25)) # A green background for the world

        self.all_sprites.draw(screen)

        if self.dialogue_to_show:
            draw_text(screen, self.dialogue_to_show, self.font, (255, 255, 255), 100, 450)

        if self.save_message_timer > 0:
            draw_text(screen, "Game Saved!", self.font, (255, 255, 0), 350, 10)

        # Draw HUD
        self._draw_hud(screen)

    def _draw_hud(self, screen):
        # Simple HUD on the bottom of the screen
        hud_rect = pygame.Rect(0, 500, 800, 100)
        pygame.draw.rect(screen, (50, 50, 50), hud_rect)

        draw_text(screen, f"HP: {self.player.hp}/{self.player.max_hp}", self.font, (255, 255, 255), 10, 510)
        draw_text(screen, f"Mana: {self.player.mana}/{self.player.max_mana}", self.font, (255, 255, 255), 10, 550)
        draw_text(screen, f"Fate: {self.player.fate}", self.font, (255, 255, 255), 200, 510)
        draw_text(screen, f"Defense: {self.player.total_defense}", self.font, (255, 255, 255), 200, 550)

        # Display spells
        draw_text(screen, "Spells:", self.font, (255, 255, 255), 400, 510)
        for i, spell in enumerate(self.player.spellbook):
            draw_text(screen, f"({i+1}) {spell.name}", self.font, (255, 255, 255), 400, 550 + i * 40)

        # Display equipped items
        draw_text(screen, "Equipped:", self.font, (255, 255, 255), 600, 510)
        weapon_name = self.player.equipped_weapon.name if self.player.equipped_weapon else "None"
        armor_name = self.player.equipped_armor.name if self.player.equipped_armor else "None"
        draw_text(screen, f"W: {weapon_name}", self.font, (255, 255, 255), 600, 550)
        draw_text(screen, f"A: {armor_name}", self.font, (255, 255, 255), 600, 580)
