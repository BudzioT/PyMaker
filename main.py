import sys

import pygame

from src.settings import settings
from src.editor import Editor


class Game:
    """Main game class"""
    def __init__(self):
        """Initialize the game"""
        # Initialize the pygame
        pygame.init()

        # Set the main surface
        self.surface = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        # Set the game timer
        self.clock = pygame.time.Clock()

        # Level editor
        self.editor = Editor()

    def run(self):
        """Run the game loop"""
        while True:
            # Delta time for FPS
            delta_time = self.clock.tick() / 1000
            # Handle events
            # self._get_events()

            # Run the editor
            self.editor.run(delta_time)

            # Update the surface
            self._update_surface()

    def _get_events(self):
        """Get the input events"""
        # Go through each event
        for event in pygame.event.get():
            # If user wants to quit, do it
            if event.type == pygame.QUIT:
                # Uninitialize pygame modules
                pygame.quit()
                # Quit
                sys.exit()

    def _update_surface(self):
        """Update the main surface and draw everything onto it"""
        pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
