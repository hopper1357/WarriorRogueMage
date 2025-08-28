import pygame
from character import Character
from combat import Combat
from ui import Button
from items import all_items
from spells import all_spells
from event_manager import event_manager

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
        self.selection_state = "main" # "main", "spell_selection", "enhancement", "fate_prompt"
        self.selected_spell = None
        self.enhancement_level = 0
        self.pending_action = None # To store the action for a potential reroll

        self.buttons = self._create_main_buttons()
        self.turn, _ = self.combat.determine_initiative()
        self.combat_log = [f"{self.turn.name} wins initiative!"]

    def _create_main_buttons(self):
        buttons = {}
        buttons["attack"] = Button(100, 450, 150, 50, "Attack", (200, 0, 0), (255, 255, 255))
        buttons["spell"] = Button(300, 450, 150, 50, "Cast Spell", (0, 0, 200), (255, 255, 255))
        buttons["dismiss"] = Button(500, 450, 150, 50, "Dismiss Spells", (0, 100, 200), (255, 255, 255))
        return buttons

    def _create_spell_buttons(self):
        buttons = {}
        for i, spell in enumerate(self.player.spellbook):
            buttons[spell.name] = Button(100 + (i % 4) * 160, 400 + (i // 4) * 60, 150, 50, spell.name, (0, 0, 200), (255, 255, 255))
        buttons["back"] = Button(650, 500, 100, 50, "Back", (200, 200, 0), (0, 0, 0))
        return buttons

    def _create_enhancement_buttons(self):
        buttons = {}
        buttons["inc"] = Button(450, 250, 40, 40, "+", (0, 255, 0), (0, 0, 0))
        buttons["dec"] = Button(500, 250, 40, 40, "-", (255, 0, 0), (0, 0, 0))
        buttons["cast"] = Button(300, 350, 200, 50, "Cast Spell", (0, 0, 200), (255, 255, 255))
        buttons["back"] = Button(650, 500, 100, 50, "Back", (200, 200, 0), (0, 0, 0))
        return buttons

    def _create_fate_buttons(self):
        buttons = {}
        buttons["yes"] = Button(300, 300, 100, 50, "Yes", (0, 200, 0), (255, 255, 255))
        buttons["no"] = Button(450, 300, 100, 50, "No", (200, 0, 0), (255, 255, 255))
        return buttons

    def handle_event(self, event):
        if self.is_over or self.turn != self.player:
            return

        if self.selection_state == "main":
            if self.buttons["attack"].is_clicked(event):
                self._player_turn("attack")
            elif self.buttons.get("spell") and self.buttons["spell"].is_clicked(event):
                self.selection_state = "spell_selection"
                self.buttons = self._create_spell_buttons()
            elif self.buttons["dismiss"].is_clicked(event):
                if self.player.sustained_spells:
                    self.player.sustained_spells.clear()
                    self.combat_log.append("You dismissed all sustained spells.")
        elif self.selection_state == "spell_selection":
            if self.buttons["back"].is_clicked(event):
                self.selection_state = "main"
                self.buttons = self._create_main_buttons()
            else:
                for spell in self.player.spellbook:
                    if self.buttons.get(spell.name) and self.buttons[spell.name].is_clicked(event):
                        self.selected_spell = spell
                        self.enhancement_level = 0
                        self.selection_state = "enhancement"
                        self.buttons = self._create_enhancement_buttons()
                        break
        elif self.selection_state == "enhancement":
            if self.buttons["inc"].is_clicked(event):
                self.enhancement_level += 1
            elif self.buttons["dec"].is_clicked(event):
                if self.enhancement_level > 0:
                    self.enhancement_level -= 1
            elif self.buttons["cast"].is_clicked(event):
                self._player_turn("spell")
            elif self.buttons["back"].is_clicked(event):
                self.selection_state = "spell_selection"
                self.buttons = self._create_spell_buttons()
        elif self.selection_state == "fate_prompt":
            if self.buttons["yes"].is_clicked(event):
                if self.player.spend_fate(1):
                    self.combat_log.append("You spend 1 Fate to reroll!")
                    self._player_turn(self.pending_action, is_reroll=True)
                else:
                    self.combat_log.append("You don't have enough Fate!")
                    self._end_player_turn()
            elif self.buttons["no"].is_clicked(event):
                self._end_player_turn()

    def _execute_player_attack(self):
        weapon = self.player.equipped_weapon or all_items["unarmed_strike"]
        success, total, damage = self.combat.attack(self.player, self.opponent, weapon)
        if success:
            self.combat_log.append(f"You hit for {damage} damage with {weapon.name}!")
        else:
            self.combat_log.append(f"You missed with {weapon.name}!")
        return success

    def _execute_player_spell(self):
        success = self.player.cast_spell(self.selected_spell, self.opponent, enhancement_level=self.enhancement_level)
        if success:
            self.combat_log.append(f"You cast {self.selected_spell.name}!")
        else:
            self.combat_log.append(f"You failed to cast {self.selected_spell.name}!")
        return success

    def _end_player_turn(self):
        self.selection_state = "main"
        self.buttons = self._create_main_buttons()
        if not self.is_over:
            self.turn = self.opponent
            self._monster_turn()

    def _check_opponent_death(self):
        if self.opponent.is_dead:
            self.winner = self.player
            self.is_over = True
            xp_gain = self.opponent.xp_value
            self.combat_log.append(f"You gained {xp_gain} XP!")
            if self.player.add_xp(xp_gain):
                self.leveled_up = True
            loot = self.opponent.drop_loot()
            if loot:
                self.player.inventory.append(loot)
                self.combat_log.append(f"You found a {loot.name}!")
            event_manager.post({"type": "monster_killed", "name": self.opponent.name})
            return True
        return False

    def _player_turn(self, action, is_reroll=False):
        success = False
        if action == "attack":
            success = self._execute_player_attack()
        elif action == "spell":
            success = self._execute_player_spell()

        if not success and self.player.fate > 0 and not is_reroll:
            self.pending_action = action
            self.selection_state = "fate_prompt"
            self.buttons = self._create_fate_buttons()
            return

        if self._check_opponent_death():
            return

        self._end_player_turn()

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
        if self.player.is_seriously_wounded:
            draw_text(screen, "Seriously Wounded!", self.font, (255, 100, 100), 100, 180)

        draw_text(screen, self.opponent.name, self.font, (255, 255, 255), 600, 100)
        draw_text(screen, f"HP: {self.opponent.hp}/{self.opponent.max_hp}", self.font, (255, 255, 255), 600, 150)
        if self.opponent.is_seriously_wounded:
            draw_text(screen, "Seriously Wounded!", self.font, (255, 100, 100), 600, 180)

        # Draw buttons
        if self.selection_state == "enhancement":
            draw_text(screen, f"Enhance {self.selected_spell.name}", self.font, (255, 255, 255), 300, 200)
            draw_text(screen, f"Level: {self.enhancement_level}", self.font, (255, 255, 255), 300, 250)

            mana_cost = self.selected_spell.mana_cost + self.enhancement_level * (self.selected_spell.mana_cost // 2)
            dl = self.selected_spell.dl + self.enhancement_level
            draw_text(screen, f"Cost: {mana_cost} Mana, DL: {dl}", self.font, (255, 255, 255), 300, 300)
        elif self.selection_state == "fate_prompt":
            draw_text(screen, "Action failed!", self.font, (255, 255, 0), 300, 200)
            draw_text(screen, f"Spend 1 Fate to reroll? (Fate: {self.player.fate})", self.font, (255, 255, 255), 300, 250)

        for button in self.buttons.values():
            button.draw(screen)

        # Draw combat log
        for i, msg in enumerate(self.combat_log[-5:]): # Show last 5 messages
            draw_text(screen, msg, self.font, (255, 255, 255), 100, 250 + i * 40)

        if self.is_over:
            winner_msg = f"{self.winner.name} wins!" if self.winner else "It's a draw!"
            draw_text(screen, winner_msg, self.font, (255, 255, 0), 300, 50)
            draw_text(screen, "Press ESC to continue", self.font, (255, 255, 255), 250, 550)
