import sys

import pygame
from pygame.math import Vector2 as vector

from src.settings import settings
from src.utilities import utilities


class Level:
    """The game's level class"""
    def __init__(self):
        """Initialize the game's level"""
        # Get the main surface
        self.surface = pygame.display.get_surface()

    def run(self, delta_time):
        """Run the game level"""
        # Handle events
        self._get_events()
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

    def _update_surface(self):
        """Update the surface"""
        self.surface.fill("white")
