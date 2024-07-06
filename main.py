import sys
import os

import pygame
from pygame.image import load

from src.settings import settings
from src.editor import Editor
from src.utilities import utilities
from src.level import Level
from src.transition import Transition


class Main:
    """Main game class"""
    def __init__(self):
        """Initialize the game"""
        # Initialize the pygame
        pygame.init()

        # Set the main surface
        self.surface = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        # Set the game timer
        self.clock = pygame.time.Clock()

        # Import the assets
        self._import_assets()

        # Load the cursor image
        cursor_img = load(os.path.join(settings.BASE_PATH, "../graphics/cursors/mouse.png")).convert_alpha()
        # Create a cursor with the loaded image
        cursor = pygame.cursors.Cursor((0, 0), cursor_img)
        # Set it as the current one
        pygame.mouse.set_cursor(cursor)

        # Level editor
        self.editor = Editor(self.land_tiles)
        # Level itself
        self.level = Level()

        # Editor active flag
        self.editor_on = True

        # Transition between editor and the level
        self.transition = Transition(self._toggle_editor)

    def run(self):
        """Run the game loop"""
        while True:
            # Delta time for FPS
            delta_time = self.clock.tick() / 1000

            # Run the editor when it's active
            if self.editor_on:
                self.editor.run(delta_time)
            # Otherwise run the level
            else:
                self.level.run(delta_time)

            # Draw the transition effect
            self.transition.display(delta_time)

            # Update the surface
            self._update_surface()

    def _update_surface(self):
        """Update the main surface and draw everything onto it"""
        pygame.display.update()

    def _import_assets(self):
        """Import all general assets"""
        # Import land tiles
        self.land_tiles = utilities.import_folder_dict("../graphics/terrain/land")

    def _toggle_editor(self):
        """Toggle the editor"""
        self.editor_on = not self.editor_on


if __name__ == "__main__":
    main = Main()
    main.run()
