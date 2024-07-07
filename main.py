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
        self.editor = Editor(self.land_tiles, self._switch)

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
        # Import bottom water tile
        self.water_bottom = (load(os.path.join(settings.BASE_PATH, "../graphics/terrain/water/water_bottom.png"))
                             .convert_alpha())
        # Get the entire water animation
        self.water_top = utilities.import_folder("../graphics/terrain/water/animation")

        # Import every coin graphic
        self.gold_coin = utilities.import_folder("../graphics/items/gold")
        self.silver_coin = utilities.import_folder("../graphics/items/silver")
        self.diamond_coin = utilities.import_folder("../graphics/items/diamond")

        # Import enemies
        # Spikes
        self.spikes = (load(os.path.join(settings.BASE_PATH, "../graphics/enemies/spikes/spikes.png"))
                       .convert_alpha())
        # Get all the tooth assets
        self.tooth = {}
        for folder in list(os.walk(os.path.join(settings.BASE_PATH, "../graphics/enemies/tooth")))[0][1]:
            # Import the tooth enemy and add it to the dictionary
            self.tooth[folder] = utilities.import_folder(f"../graphics/enemies/tooth/{folder}")

        # Get shells assets (only for the left one, to get the right one just flip it)
        self.shell = {}
        for folder in list(os.walk(os.path.join(settings.BASE_PATH, "../graphics/enemies/shell_left")))[0][1]:
            self.shell[folder] = utilities.import_folder(f"../graphics/enemies/shell_left/{folder}")

        # Palm assets dictionary
        self.palms = {}
        # Go through each of the palm folders and then import them
        for folder in list(os.walk(os.path.join(settings.BASE_PATH, "../graphics/terrain/palm")))[0][1]:
            # Import the palm, add it to the dictionary
            self.palms[folder] = utilities.import_folder(f"../graphics/terrain/palm/{folder}")

        # Import the particles
        self.particle = utilities.import_folder("../graphics/items/particle")

    def _toggle_editor(self):
        """Toggle the editor"""
        self.editor_on = not self.editor_on

    def _switch(self, grid=None):
        """Switch between the level and the editor, saving the map"""
        # Turn on the transition
        self.transition.active = True

        # If a grid exists
        if grid:
            self.level = Level(grid, self._switch, {
                # Terrains
                "land": self.land_tiles,
                "water_bottom": self.water_bottom,
                "water_top": self.water_top,

                # Coins
                "gold_coin": self.gold_coin,
                "silver_coin": self.silver_coin,
                "diamond_coin": self.diamond_coin,

                # Enemies
                "spikes": self.spikes,
                "tooth": self.tooth,
                "shell": self.shell,

                # All the palms
                "palms": self.palms,

                # Particles
                "particle": self.particle
            })


if __name__ == "__main__":
    main = Main()
    main.run()
