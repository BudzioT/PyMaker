import os

import pygame

from src.settings import settings


class UI:
    """User's interface of the game"""
    def __init__(self):
        """Initialize the user's interface"""
        # Grab the main surface
        self.surface = pygame.display.get_surface()

        # Create a new font
        self.font = pygame.font.Font(os.path.join(settings.BASE_PATH, settings.FONT), settings.FONT_SIZE)

        # Create health bar
        self.health_bar_rect = pygame.Rect(10, 10, settings.HEALTH_BAR_WIDTH, settings.HEALTH_BAR_HEIGHT)

    def display(self, player):
        """Display the user's interface"""
        # Show the health bar
        self._show_bar(player.health, 6, self.health_bar_rect, settings.HEALTH_COLOR)

        # Show the current coins
        self._show_coins(player.coins)

    def _show_bar(self, current_amount, max_amount, bg_rect, color):
        """Show a bar with given information"""
        # Draw the background
        pygame.draw.rect(self.surface, settings.BG_COLOR, bg_rect)

        # Calculate ratio of health and get bar's width from it
        ratio = current_amount / max_amount
        current_width = bg_rect.width * ratio
        # Copy the background's rectangle and change its width to the current amount's width
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        # Draw the current amount bar
        pygame.draw.rect(self.surface, color, current_rect)
        # Draw the bar's border
        pygame.draw.rect(self.surface, settings.BORDER_COLOR, bg_rect, 3)

    def _show_coins(self, coins):
        """Show player's coins"""
        # Render the text
        text_surface = self.font.render(str(int(coins)), False, settings.TEXT_COLOR)

        # Calculate position of coins text
        pos_x = settings.WINDOW_WIDTH - 20
        pos_y = settings.WINDOW_HEIGHT - 20
        # Create the coins text rectangle
        text_rect = text_surface.get_rect(bottomright=(pos_x, pos_y))

        # Draw the coin's background
        pygame.draw.rect(self.surface, settings.BG_COLOR, text_rect.inflate(10, 10))
        # Blit the text onto the main surface
        self.surface.blit(text_surface, text_rect)
        # Draw the frame
        pygame.draw.rect(self.surface, settings.BORDER_COLOR, text_rect.inflate(10, 10), 3)
