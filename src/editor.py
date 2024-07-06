import sys

import pygame
from pygame.math import Vector2 as vector
from pygame.mouse import get_pressed as mouse_pressed
from pygame.mouse import get_pos as mouse_pos

from src.settings import settings
from src.menu import Menu
from src.MapTile import MapTile


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

        # Map data
        self.map_data = {}

        # Last clicked cell
        self.last_cell = None

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

            # Handle menu clicks
            self._menu_click(event)
            # Handle clicks outside of menu
            self._map_add()

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
            # Save the selection index
            self.select_index = self.menu.handle_click(mouse_pos(), mouse_pressed())

    def _get_current_cell(self):
        """Get the current cell"""
        # Get the distance between the mouse position and the map origin
        distance_origin = vector(mouse_pos()) - self.origin

        # If horizontal distance is higher than 0, just get its tile column
        if distance_origin.x > 0:
            column = int(distance_origin.x / settings.TILE_SIZE)
        # Otherwise subtract one, to prevent two tiles with the same tile position
        else:
            column = int(distance_origin.x / settings.TILE_SIZE) - 1

        # If vertical distance is below the origin, set the row to the tile
        if distance_origin.y > 0:
            row = int(distance_origin.y / settings.TILE_SIZE)
        # Otherwise subtract one again
        else:
            row = int(distance_origin.y / settings.TILE_SIZE) - 1

        # Return the cell's position
        return column, row

    # Drawing
    def _update_surface(self):
        """Update and draw everything onto the main surface"""
        self.surface.fill("white")

        # Draw the map
        self.draw_map()

        # Draw the tile lines
        self._draw_lines()

        # Draw a circle
        pygame.draw.circle(self.surface, "red", self.origin, 10)

        # Display the menu
        self.menu.display(self.select_index)

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

    def draw_map(self):
        """Draw the map"""
        # Go through each tile placed
        for cell_pos, tile in self.map_data.items():
            # Get its position in pixels
            pos = self.origin + vector(cell_pos) * settings.TILE_SIZE

            # If tile has water
            if tile.water:
                test_surface = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE))
                test_surface.fill("blue")
                self.surface.blit(test_surface, pos)

            # If it has terrain
            if tile.terrain:
                test_surface = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE))
                test_surface.fill("brown")
                self.surface.blit(test_surface, pos)

            # If it has a coin
            if tile.coin:
                test_surface = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE))
                test_surface.fill("yellow")
                self.surface.blit(test_surface, pos)

            # Otherwise if it has an enemy
            if tile.enemy:
                test_surface = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE))
                test_surface.fill("red")
                self.surface.blit(test_surface, pos)


    def _map_add(self):
        """Add the item to the map"""
        # If user pressed the left mouse button but didn't click on the menu
        if mouse_pressed()[0] and not self.menu.rect.collidepoint(mouse_pos()):
            # Get the current clicked cell
            current_cell = self._get_current_cell()

            # If user didn't click on the same cell twice
            if current_cell != self.last_cell:
                # If there is something already, change the cell to the current ID
                if current_cell in self.map_data:
                    self.map_data[current_cell].add_id(self.select_index)

                # Otherwise add new cell to the map data
                else:
                    self.map_data[current_cell] = MapTile(self.select_index)

                # Save the current cell, as the last one
                self.last_cell = current_cell
