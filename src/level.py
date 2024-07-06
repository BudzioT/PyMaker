import sys

import pygame
from pygame.math import Vector2 as vector

from src.settings import settings
from src.utilities import utilities
from src.sprites import GenericSprite
from src.sprites import Player


class Level:
    """The game's level class"""
    def __init__(self, grid, switch, assets):
        """Initialize the game's level"""
        # Get the main surface
        self.surface = pygame.display.get_surface()

        # Switch between the editor and level
        self.switch = switch

        # Group with all the sprites
        self.sprites = pygame.sprite.Group()

        # Build the level based off the grid
        self._build_level(grid, assets)

    def run(self, delta_time):
        """Run the game level"""
        # Handle events
        self._get_events()

        # Update positions
        self._update_pos(delta_time)

        # Update the surface
        self._update_surface()

    def _get_events(self):
        """Get and handle the events"""
        # Go through every event
        for event in pygame.event.get():
            # If user wants to quit, free the pygame resources and exit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # If user clicks escape, switch to the editor
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch()

    def _update_pos(self, delta_time):
        """Update positions of elements"""
        # Update the player's position
        self.sprites.update(delta_time)

    def _update_surface(self):
        """Update the surface"""
        # Draw the sky
        self.surface.fill(settings.COLORS["SKY"])
        # Draw all the sprites
        self.sprites.draw(self.surface)

    def _build_level(self, grid, assets):
        """Build the level based off the grid using the given assets"""
        # Go through every single one of grid layers
        for layer_name, layer in grid.items():
            # Check all the layer placements
            for pos, data in layer.items():
                # If this layer is terrain, create a sprite with land at saved position
                if layer_name == "terrain":
                    GenericSprite(pos, assets["land"][data], self.sprites)

                # Check if layer is water one
                if layer_name == "water":
                    # If the tile is top one, create the water top tile with animation
                    if data == "top":
                        pass
                    # Otherwise create the bottom, plain one
                    else:
                        GenericSprite(pos, assets["water_bottom"], self.sprites)

                # If layer's ID was 0, place the player
                if data == 0:
                    self.player = Player(pos, self.sprites)
