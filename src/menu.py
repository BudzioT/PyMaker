import os

import pygame
from pygame.image import load

from src.settings import settings


class Menu:
    """The editor's menu"""
    def __init__(self):
        """Initialize the editor's menu"""
        # Get the main surface
        self.surface = pygame.display.get_surface()

        # Get the data for menu
        self._get_data()

        # Create the entire menu
        self._create_menu()

    # Drawing
    def display(self):
        """Display the menu"""
        # Draw the menu area
        pygame.draw.rect(self.surface, "red", self.rect)

        # Update the buttons
        self.buttons.update()

        # Draw the buttons
        pygame.draw.rect(self.surface, "green", self.tile_button_rect)
        pygame.draw.rect(self.surface, "green", self.enemy_button_rect)
        pygame.draw.rect(self.surface, "green", self.coin_button_rect)
        pygame.draw.rect(self.surface, "green", self.palm_button_rect)

    def _create_menu(self):
        """Create the menu"""
        # Menu size and margin
        size = 180
        margin = 6
        # Menu top left position
        top_left = (settings.WINDOW_WIDTH - size - margin, settings.WINDOW_HEIGHT - size - margin)
        # Menu rectangle
        self.rect = pygame.Rect(top_left, (size, size))

        self._create_buttons()

    def _create_buttons(self):
        """Create the buttons"""
        # Generic button area
        button_rect = pygame.Rect(self.rect.topleft, (self.rect.width / 2, self.rect.height / 2))
        # Margin of buttons
        margin = 5

        # Tile button rectangle (inflate for margin)
        self.tile_button_rect = button_rect.copy().inflate(-margin, -margin)
        # Enemy button rectangle, placed next to the tile one
        self.enemy_button_rect = button_rect.move(self.rect.width / 2, 0).inflate(-margin, -margin)
        # Coin rectangle, that is below the tile button
        self.coin_button_rect = button_rect.move(0, self.rect.height / 2).inflate(-margin, -margin)
        # Palm rectangle, with placement next to the coin button
        self.palm_button_rect = (
            button_rect.move(self.rect.width / 2, self.rect.height / 2).inflate(-margin, -margin))

        # Buttons group
        self.buttons = pygame.sprite.Group()
        # Create all the buttons
        Button(self.tile_button_rect, self.buttons, self.menu_surfaces["terrain"])
        Button(self.enemy_button_rect, self.buttons, self.menu_surfaces["enemy"])
        Button(self.coin_button_rect, self.buttons, self.menu_surfaces["coin"])
        Button(self.palm_button_rect, self.buttons, self.menu_surfaces["palm fg"], self.menu_surfaces["palm bg"])

    def handle_click(self):
        """Handle user's clicks"""
        print("Clicked menu")

    def _get_data(self):
        """Get the data from dictionary"""
        self.menu_surfaces = {}
        # Go through each item in the editor's dictionary
        for item_id, item in settings.EDITOR_INFO.items():
            # Check if the item should be displayed in menu
            if item["menu"]:
                # If there isn't certain category added yet, add it
                if not item["menu"] in self.menu_surfaces:
                    # Load the image into the list
                    self.menu_surfaces[item["menu"]] = [(item_id, load(os.path.join(settings.BASE_PATH,
                                                                                    item["menu_surf"])))]
                # Otherwise just append another image
                else:
                    self.menu_surfaces[item["menu"]].append((item_id, load(os.path.join(settings.BASE_PATH,
                                                                                        item["menu_surf"]))))


class Button(pygame.sprite.Sprite):
    """Class representing a button"""
    def __init__(self, rect, group, items, alt_items = None):
        """Initialize the button"""
        super().__init__(group)
        # Create the button image and get its rect
        self.image = pygame.Surface(rect.size)
        self.rect = rect

        # Item index
        self.index = 0
        # List of items
        self.items = {"main": items, "alt": alt_items}
        # Flag that tells if the user is in the main items
        self.main = True

    # Drawing
    def update(self):
        """Update and draw the button"""
        # Draw the background
        self.image.fill(settings.COLORS["BUTTON"])
        # Set the surface depending on, if the user chose main or alternate items
        surface = self.items["main" if self.main else "alt"][self.index][1]

        # Get the button's rectangle
        rect = surface.get_rect(center=(self.rect.width / 2, self.rect.height / 2))
        # Blit the current button image
        self.image.blit(surface, rect)
