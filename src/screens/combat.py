import pygame
from character import Character
from combat import Combat
from ui import Button
from items import all_items

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

class CombatScreen:
    def __init__(self, player, opponent):
        self.player = player
        self.opponent = opponent
        self.combat = Combat(player, opponent)
        self.font = pygame.font.Font(None, 36)
        self.is_over = False
        self.winner = None
        self.leveled_up = False

        self.buttons = self._create_buttons()
        self.turn, _ = self.combat.determine_initiative()
        self.combat_log = [f"{self.turn.name} wins initiative!"]

    def _create_buttons(self):
        buttons = {}
        buttons["attack"] = Button(100, 450, 150, 50, "Attack", (200, 0, 0), (255, 255, 255))
        # Add more buttons for spells, items, flee later
        return buttons

    def handle_event(self, event):
        if self.turn == self.player:
            if self.buttons["attack"].is_clicked(event):
                self._player_turn("attack")

    def _player_turn(self, action):
        if action == "attack":
            weapon = self.player.equipped_weapon or all_items["unarmed_strike"]
            success, total, damage = self.combat.attack(self.player, self.opponent, weapon)
            if success:
                self.combat_log.append(f"You hit for {damage} damage with {weapon.name}!")
            else:
                self.combat_log.append(f"You missed with {weapon.name}!")

        if self.opponent.is_dead:
            self.winner = self.player
            self.is_over = True
            # XP
            xp_gain = self.opponent.xp_value
            self.combat_log.append(f"You gained {xp_gain} XP!")
            if self.player.add_xp(xp_gain):
                self.leveled_up = True
            # Loot
            loot = self.opponent.drop_loot()
            if loot:
                self.player.inventory.append(loot)
                self.combat_log.append(f"You found a {loot.name}!")

        self.turn = self.opponent
        self._monster_turn()

    def _monster_turn(self):
        if self.is_over: return

        weapon = self.opponent.equipped_weapon or all_items["unarmed_strike"]
        success, total, damage = self.combat.attack(self.opponent, self.player, weapon)
        if success:
            self.combat_log.append(f"{self.opponent.name} hits for {damage} damage with {weapon.name}!")
        else:
            self.combat_log.append(f"{self.opponent.name} missed with {weapon.name}!")

        if self.player.is_dead:
            self.winner = self.opponent
            self.is_over = True

        self.turn = self.player

    def update(self):
        # The combat is turn-based, so update is mostly driven by events
        pass

    def draw(self, screen):
        screen.fill((50, 0, 0)) # Dark red background for combat

        # Draw combatants
        draw_text(screen, self.player.name, self.font, (255, 255, 255), 100, 100)
        draw_text(screen, f"HP: {self.player.hp}/{self.player.max_hp}", self.font, (255, 255, 255), 100, 150)

        draw_text(screen, self.opponent.name, self.font, (255, 255, 255), 600, 100)
        draw_text(screen, f"HP: {self.opponent.hp}/{self.opponent.max_hp}", self.font, (255, 255, 255), 600, 150)

        # Draw buttons
        for button in self.buttons.values():
            button.draw(screen)

        # Draw combat log
        for i, msg in enumerate(self.combat_log[-5:]): # Show last 5 messages
            draw_text(screen, msg, self.font, (255, 255, 255), 100, 250 + i * 40)

        if self.is_over:
            winner_msg = f"{self.winner.name} wins!" if self.winner else "It's a draw!"
            draw_text(screen, winner_msg, self.font, (255, 255, 0), 300, 50)
            draw_text(screen, "Press ESC to continue", self.font, (255, 255, 255), 250, 550)
