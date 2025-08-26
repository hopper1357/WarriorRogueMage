import pygame
import sys
from enum import Enum
from character import Character
from screens.character_creation import CharacterCreationScreen
from screens.gameplay import GameplayScreen
from screens.combat import CombatScreen

class GameState(Enum):
    CHARACTER_CREATION = 1
    GAMEPLAY = 2
    COMBAT = 3

def main():
    pygame.init()

    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Warrior Rogue Mage")

    game_state = GameState.CHARACTER_CREATION
    creation_screen = CharacterCreationScreen()
    gameplay_screen = None
    combat_screen = None
    player = None
    active_monster = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == GameState.CHARACTER_CREATION:
                creation_screen.handle_event(event)
            elif game_state == GameState.GAMEPLAY:
                gameplay_screen.handle_event(event)
            elif game_state == GameState.COMBAT:
                combat_screen.handle_event(event)
                if combat_screen.is_over and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Remove the defeated monster
                    if combat_screen.winner == player:
                        active_monster.kill()
                    game_state = GameState.GAMEPLAY
                    combat_screen = None


        screen.fill((0,0,0))

        if game_state == GameState.CHARACTER_CREATION:
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

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
