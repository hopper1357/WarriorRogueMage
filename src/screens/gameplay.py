import pygame
from character import Character
from entities import TownGuard, Goblin, GiantRat, Skeleton, Bandit, GiantSpider, BanditLeader
from save_manager import save_game
from tilemap import Map, Camera
from event_manager import event_manager
from ui import Button

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

class GameplayScreen:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.Font(None, 36)

        self.map = Map("town.txt")
        self.camera = Camera(self.map.width, self.map.height)

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)

        self.npcs = pygame.sprite.Group()
        guard = TownGuard(x=10 * 32, y=5 * 32) # Place entities on the map grid
        self.all_sprites.add(guard)
        self.npcs.add(guard)

        self.monsters = pygame.sprite.Group()
        goblin = Goblin(x=15 * 32, y=12 * 32)
        rat = GiantRat(x=5 * 32, y=14 * 32)
        skeleton = Skeleton(x=15 * 32, y=3 * 32)
        bandit = Bandit(x=3 * 32, y=3 * 32)
        spider = GiantSpider(x=17 * 32, y=8 * 32)
        bandit_leader = BanditLeader(x=18 * 32, y=2 * 32)
        self.all_sprites.add(goblin, rat, skeleton, bandit, spider, bandit_leader)
        self.monsters.add(goblin, rat, skeleton, bandit, spider, bandit_leader)

        self.player_speed = 5
        self.dialogue_to_show = None
        self.active_monster = None
        self.save_message_timer = 0
        self.rest_message = ""
        self.rest_message_timer = 0
        self.hazard_message = ""
        self.hazard_message_timer = 0
        self.hazard_cooldown = 0

        self.rest_button = Button(700, 10, 90, 40, "Rest", (0, 100, 0), (255, 255, 255))

        self._subscribe_quests()

    def _subscribe_quests(self):
        for quest in self.player.journal:
            for objective in quest.objectives:
                event_manager.subscribe("monster_killed", objective.update)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                if len(self.player.spellbook) > 0:
                    self.player.cast_spell(self.player.spellbook[0], self.player) # Target self for now
            elif event.key == pygame.K_2:
                if len(self.player.spellbook) > 1:
                    self.player.cast_spell(self.player.spellbook[1], self.player)
            elif event.key == pygame.K_i:
                from main import GameState
                return GameState.INVENTORY
            elif event.key == pygame.K_F5:
                save_game(self.player)
                self.save_message_timer = 120
            elif event.key == pygame.K_j:
                from main import GameState
                return GameState.JOURNAL
            elif event.key == pygame.K_d:
                if self.player.sustained_spells:
                    self.player.sustained_spells.clear()
                    print("You have dismissed all sustained spells.")

        if self.rest_button.is_clicked(event):
            hp_before = self.player.hp
            mana_before = self.player.mana
            self.player.rest()
            hp_recovered = self.player.hp - hp_before
            mana_recovered = self.player.mana - mana_before
            self.rest_message = f"Rested. HP +{hp_recovered}, Mana +{mana_recovered}"
            self.rest_message_timer = 120 # Show message for 2 seconds

        return None

    def update(self, screen):
        # Player movement
        vx, vy = 0, 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vx = -self.player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vx = self.player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            vy = -self.player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vy = self.player_speed

        self.player.rect.x += vx
        self.check_collisions('x')
        self.player.rect.y += vy
        self.check_collisions('y')

        self.camera.update(self.player)

        if self.save_message_timer > 0:
            self.save_message_timer -= 1

        if self.rest_message_timer > 0:
            self.rest_message_timer -= 1

        if self.hazard_message_timer > 0:
            self.hazard_message_timer -= 1

        if self.hazard_cooldown > 0:
            self.hazard_cooldown -= 1

        # Hazard collision logic
        if self.hazard_cooldown == 0:
            hits = pygame.sprite.spritecollide(self.player, self.map.hazards, False)
            if hits:
                hazard = hits[0]
                hp_before = self.player.hp
                self.player.take_damage(hazard.damage, hazard.damage_type)
                damage_taken = hp_before - self.player.hp
                self.hazard_message = f"Took {damage_taken} {hazard.damage_type} damage!"
                self.hazard_message_timer = 120 # Show message for 2 seconds
                self.hazard_cooldown = 60 # 1 second cooldown

        # Interaction logic
        self.dialogue_to_show = None
        for npc in self.npcs:
            if self.player.rect.colliderect(npc.rect.inflate(20, 20)):
                self.dialogue_to_show = npc.interact(self.player)
                break

        for monster in self.monsters:
            if self.player.rect.colliderect(monster.rect.inflate(20, 20)):
                self.active_monster = monster
                from main import GameState
                return GameState.COMBAT, self.active_monster

        from main import GameState
        return GameState.GAMEPLAY, None

    def check_collisions(self, direction):
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self.player, self.map.walls, False)
            if hits:
                if self.player.rect.x > hits[0].rect.x: # Moving left
                    self.player.rect.left = hits[0].rect.right
                else: # Moving right
                    self.player.rect.right = hits[0].rect.left
        if direction == 'y':
            hits = pygame.sprite.spritecollide(self.player, self.map.walls, False)
            if hits:
                if self.player.rect.y > hits[0].rect.y: # Moving up
                    self.player.rect.top = hits[0].rect.bottom
                else: # Moving down
                    self.player.rect.bottom = hits[0].rect.top

    def draw(self, screen):
        screen.fill((25, 100, 25))

        for sprite in self.map.all_tiles:
            screen.blit(sprite.image, self.camera.apply(sprite))

        for sprite in self.all_sprites:
            screen.blit(sprite.image, self.camera.apply(sprite))

        if self.dialogue_to_show:
            draw_text(screen, self.dialogue_to_show, self.font, (255, 255, 255), 100, 450)

        if self.save_message_timer > 0:
            draw_text(screen, "Game Saved!", self.font, (255, 255, 0), 350, 10)

        if self.rest_message_timer > 0:
            draw_text(screen, self.rest_message, self.font, (173, 216, 230), 250, 50)

        if self.hazard_message_timer > 0:
            draw_text(screen, self.hazard_message, self.font, (255, 100, 100), 250, 80)

        self.rest_button.draw(screen)
        self._draw_hud(screen)

    def _draw_hud(self, screen):
        hud_rect = pygame.Rect(0, 500, 800, 100)
        pygame.draw.rect(screen, (50, 50, 50), hud_rect)

        draw_text(screen, f"HP: {self.player.hp}/{self.player.max_hp}", self.font, (255, 255, 255), 10, 510)
        draw_text(screen, f"Mana: {self.player.mana}/{self.player.max_mana}", self.font, (255, 255, 255), 10, 550)
        draw_text(screen, f"Fate: {self.player.fate}", self.font, (255, 255, 255), 200, 510)
        draw_text(screen, f"Defense: {self.player.total_defense}", self.font, (255, 255, 255), 200, 550)

        draw_text(screen, "Spells:", self.font, (255, 255, 255), 400, 510)
        for i, spell in enumerate(self.player.spellbook):
            draw_text(screen, f"({i+1}) {spell.name}", self.font, (255, 255, 255), 400, 550 + i * 40)

        draw_text(screen, "Equipped:", self.font, (255, 255, 255), 600, 510)
        weapon_name = self.player.equipped_weapon.name if self.player.equipped_weapon else "None"
        body_armor_name = self.player.equipped_body_armor.name if self.player.equipped_body_armor else "None"
        shield_name = self.player.equipped_shield.name if self.player.equipped_shield else "None"
        implement_name = self.player.equipped_implement.name if self.player.equipped_implement else "None"
        draw_text(screen, f"W: {weapon_name}", self.font, (255, 255, 255), 600, 550)
        draw_text(screen, f"B: {body_armor_name}", self.font, (255, 255, 255), 600, 580)
        draw_text(screen, f"S: {shield_name}", self.font, (255, 255, 255), 600, 610)
        if self.player.equipped_implement:
            draw_text(screen, f"I: {implement_name} ({self.player.equipped_implement.mana_pool}/{self.player.equipped_implement.max_mana})", self.font, (255, 255, 255), 400, 580)

        # Display sustained spells
        if self.player.sustained_spells:
            penalty = self.player.get_sustained_penalty()
            draw_text(screen, f"Sustained (Penalty: {penalty})", self.font, (255, 100, 100), 10, 480)
