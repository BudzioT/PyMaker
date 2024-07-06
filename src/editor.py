import sys

import pygame
from pygame.math import Vector2 as vector
from pygame.mouse import get_pressed as mouse_pressed
from pygame.mouse import get_pos as mouse_pos

from src.settings import settings
from src.menu import Menu


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

        # Surface of support lines
        self.support_surface = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        # Set its color key as green
        self.support_surface.set_colorkey("green")
        # Set alpha of everything visible to 40
        self.support_surface.set_alpha(40)

        # Object select index
        self.select_index = 2

        # Create the menu
        self.menu = Menu()

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
            self._pan_input(event)
            # Check for select input
            self._select(event)

    def _pan_input(self, event):
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

    def _select(self, event):
        """Select the items"""
        # Check for a key press
        if event.type == pygame.KEYDOWN:
            # If user pressed right, increase the selection index
            if event.type == pygame.K_d or event.type == pygame.K_RIGHT:
                self.select_index += 1
            # If user pressed left, decrease it
            if event.type == pygame.K_a or event.type == pygame.K_LEFT:
                self.select_index -= 1
        # Don't allow the user to change index below 0
        self.select_index = max(self.select_index, 0)
        # Don't allow him to change it to high too
        self.select_index = min(self.select_index, len(settings.EDITOR_INFO))

    def _menu_click(self, event):
        """Handle menu clicks"""
        # If the user clicked the moused and the cursor is on the menu, handle the click
        if event.type == pygame.MOUSEBUTTONDOWN and self.menu.rect.collidepoint(mouse_pos()):
            self.menu.handle_click()

    # Drawing
    def _update_surface(self):
        """Update and draw everything onto the main surface"""
        self.surface.fill("white")

        # Draw the tile lines
        self._draw_lines()

        # Draw a circle
        pygame.draw.circle(self.surface, "red", self.origin, 10)

        # Display the menu
        self.menu.display()

    def _draw_lines(self):
        """Draw the tile lines"""
        # Calculate the amount of columns and rows
        columns = settings.WINDOW_WIDTH // settings.TILE_SIZE
        rows = settings.WINDOW_HEIGHT // settings.TILE_SIZE

        # Make the surface green to help with transparency
        self.support_surface.fill("green")

        # Offset to keep the lines in screen
        origin_offset = vector(self.origin.x - int(self.origin.x / settings.TILE_SIZE) * settings.TILE_SIZE,
                               self.origin.y - int(self.origin.y / settings.TILE_SIZE) * settings.TILE_SIZE)

        # Go through each column (added one because one column on the right doesn't get drawn)
        for col in range(columns + 1):
            # Calculate the vertical position by the tile size and offset them by column number from origin
            pos_x = origin_offset.x + col * settings.TILE_SIZE
            # Draw the column line
            pygame.draw.line(self.support_surface, settings.COLORS["LINE"],
                             (pos_x, 0), (pos_x, settings.WINDOW_HEIGHT))
        # Go through each row
        for row in range(rows + 1):
            # Calculate the horizontal position
            pos_y = origin_offset.y + row * settings.TILE_SIZE
            # Draw the row line
            pygame.draw.line(self.support_surface, settings.COLORS["LINE"],
                             (0, pos_y), (settings.WINDOW_WIDTH, pos_y))

        # Blit the support lines onto the main surface
        self.surface.blit(self.support_surface, (0, 0))
