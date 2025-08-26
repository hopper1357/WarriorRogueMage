import pygame
import sys
from enum import Enum
from character import Character
from screens.main_menu import MainMenuScreen
from screens.character_creation import CharacterCreationScreen
from screens.gameplay import GameplayScreen
from screens.combat import CombatScreen
from screens.inventory import InventoryScreen
from save_manager import load_game, save_game

class GameState(Enum):
    MAIN_MENU = 0
    CHARACTER_CREATION = 1
    GAMEPLAY = 2
    COMBAT = 3
    INVENTORY = 4

def main():
    pygame.init()

    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Warrior Rogue Mage")

    game_state = GameState.MAIN_MENU
    main_menu_screen = MainMenuScreen()
    creation_screen = None
    gameplay_screen = None
    combat_screen = None
    inventory_screen = None
    player = None
    active_monster = None

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == GameState.MAIN_MENU:
                main_menu_screen.handle_event(event)
            elif game_state == GameState.CHARACTER_CREATION:
                creation_screen.handle_event(event)
            elif game_state == GameState.GAMEPLAY:
                new_state = gameplay_screen.handle_event(event)
                if new_state == GameState.INVENTORY:
                    inventory_screen = InventoryScreen(player)
                    game_state = new_state
            elif game_state == GameState.COMBAT:
                combat_screen.handle_event(event)
                if combat_screen.is_over and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if combat_screen.winner == player:
                        active_monster.kill()
                    game_state = GameState.GAMEPLAY
                    combat_screen = None
            elif game_state == GameState.INVENTORY:
                inventory_screen.handle_event(event)
                if inventory_screen.is_done:
                    game_state = GameState.GAMEPLAY
                    inventory_screen = None

        # State transitions and drawing
        screen.fill((0,0,0))

        if game_state == GameState.MAIN_MENU:
            main_menu_screen.update()
            main_menu_screen.draw(screen)
            if main_menu_screen.selected_option == "new_game":
                creation_screen = CharacterCreationScreen()
                game_state = GameState.CHARACTER_CREATION
            elif main_menu_screen.selected_option == "load_game":
                player = load_game()
                if player:
                    gameplay_screen = GameplayScreen(player)
                    game_state = GameState.GAMEPLAY
                else: # If load fails, go back to menu
                    main_menu_screen.selected_option = None
            elif main_menu_screen.selected_option == "quit":
                running = False

        elif game_state == GameState.CHARACTER_CREATION:
            creation_screen.update()
            creation_screen.draw(screen)
            if creation_screen.is_done:
                player = creation_screen.character
                gameplay_screen = GameplayScreen(player)
                game_state = GameState.GAMEPLAY

        elif game_state == GameState.GAMEPLAY:
            new_state, active_monster = gameplay_screen.update(screen)
            if new_state == GameState.COMBAT:
                combat_screen = CombatScreen(player, active_monster)
            game_state = new_state
            gameplay_screen.draw(screen)

        elif game_state == GameState.COMBAT:
            combat_screen.update()
            combat_screen.draw(screen)

        elif game_state == GameState.INVENTORY:
            inventory_screen.update()
            inventory_screen.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
