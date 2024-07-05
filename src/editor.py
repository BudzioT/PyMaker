import sys

import pygame
from pygame.math import Vector2 as vector
from pygame.mouse import get_pressed as mouse_pressed
from pygame.mouse import get_pos as mouse_pos

from src.settings import settings


class Editor:
    """The game's level editor"""
    def __init__(self):
        """Initialize the editor"""
        # Get the main surface
        self.surface = pygame.display.get_surface()

        # Navigation origin
        self.origin = vector()
        # Pan active flag
        self.pan = False
        # Its offset
        self.pan_offset = vector()

    def run(self, delta_time):
        """Run the level editor"""
        # Run the event loop
        self._get_events()

        # Update the surface
        self._update_surface()

    # Input
    def _get_events(self):
        """Get the editor's input events"""
        # Go through each event that happened
        for event in pygame.event.get():
            # If user wants to quit, close the game
            if event.type == pygame.QUIT:
                # Uninitialize pygame modules
                pygame.quit()
                # Quit
                sys.exit()
            # Check and handle panning inputs
            self.pan_input(event)

    def pan_input(self, event):
        """Get panning input"""
        # If middle button is pressed, activate panning
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_pressed()[1]:
            self.pan = True
            # Calculate the offset between mouse and the origin point
            self.pan_offset = vector(mouse_pos()) - self.origin

        # If middle button is released set panning to false
        if not mouse_pressed()[1]:
            self.pan = False

        # If event is mouse wheel scroll
        if event.type == pygame.MOUSEWHEEL:
            # If user is holding left control, move the Y-Axis of the map by scrolling
            if pygame.key.get_pressed()[pygame.K_LCTRL]:
                self.origin.y -= event.y * 50
            # Otherwise move the X-Axis of the map
            else:
                # Scroll the map with it
                self.origin.x -= event.y * 50

        # If user is panning, move the origin to the same direction but with offset
        if self.pan:
            self.origin = vector(mouse_pos()) - self.pan_offset

    # Drawing
    def _update_surface(self):
        """Update and draw everything onto the main surface"""
        self.surface.fill("white")

        # Draw a circle
        pygame.draw.circle(self.surface, "red", self.origin, 10)

    def draw_lines(self):
        """Draw the tile lines"""
        # Calculate the amount of columns and rows
        columns = settings.WINDOW_WIDTH // settings.TILE_SIZE
        rows = settings.WINDOW_HEIGHT // settings.TILE_SIZE

        # Go through each column
        for col in range(columns):
            
