import pygame
import sys
from enum import Enum
from character import Character
from screens.character_creation import CharacterCreationScreen
from screens.gameplay import GameplayScreen

class GameState(Enum):
    CHARACTER_CREATION = 1
    GAMEPLAY = 2

def main():
    pygame.init()

    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Warrior Rogue Mage")

    game_state = GameState.CHARACTER_CREATION
    creation_screen = CharacterCreationScreen()
    gameplay_screen = None
    player = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == GameState.CHARACTER_CREATION:
                creation_screen.handle_event(event)
            elif game_state == GameState.GAMEPLAY:
                gameplay_screen.handle_event(event)

        screen.fill((0,0,0))

        if game_state == GameState.CHARACTER_CREATION:
            creation_screen.update()
            creation_screen.draw(screen)
            if creation_screen.is_done:
                player = creation_screen.character
                gameplay_screen = GameplayScreen(player)
                game_state = GameState.GAMEPLAY
        elif game_state == GameState.GAMEPLAY:
            gameplay_screen.update()
            gameplay_screen.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
