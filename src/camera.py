import pygame
from pygame.math import Vector2 as vector

from src.settings import settings


class CameraGroup(pygame.sprite.Group):
    """Group of sprites within camera"""
    def __init__(self):
        """Initialize the camera group"""
        super().__init__()

        # Get game's surface
        self.surface = pygame.display.get_surface()
        # Offset of the camera
        self.offset = vector()

    def custom_draw(self, player):
        """Draw everything based off the player's position"""
        # Update the offset from the player's position, center it
        self.offset.x = player.rect.centerx - settings.WINDOW_WIDTH / 2
        self.offset.y = player.rect.centery - settings.WINDOW_HEIGHT / 2

        # Draw the horizon before any other sprites
        self.draw_horizon()

        # Draw the clouds next
        for sprite in self:
            # Check if it's a cloud
            if sprite.pos_z == settings.LAYERS_DEPTH["clouds"]:
                # Calculate its offset and blit it
                offset_rect = sprite.rect.copy()
                offset_rect.center -= self.offset
                self.surface.blit(sprite.image, offset_rect)

        # Go through each of sprite within this group
        for sprite in self:
            # Go through each possible layer depth value, starting from the most background ones
            for layer_depth in settings.LAYERS_DEPTH.values():
                # If layer position is right, handle the sprite drawing
                if sprite.pos_z == layer_depth and sprite.pos_z != settings.LAYERS_DEPTH["clouds"]:
                    # Get this sprite rectangle
                    rect = sprite.rect.copy()
                    # Apply offset to it
                    rect.center -= self.offset

                    # Blit this sprite
                    self.surface.blit(sprite.image, rect)

    def draw_horizon(self):
        """Draw the horizon"""
        # Get the horizon position
        horizon_pos = self.horizon_y - self.offset.y

        # If horizon is visible, draw it
        if horizon_pos < settings.WINDOW_HEIGHT:
            # Get the sea rectangle
            sea_rect = pygame.Rect(0, horizon_pos, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT - horizon_pos)
            # Draw the sea
            pygame.draw.rect(self.surface, settings.COLORS["SEA"], sea_rect)

            # Calculate the horizon lines positions
            horizon_rect_1 = pygame.Rect(0, horizon_pos - 2, settings.WINDOW_WIDTH, 10)
            horizon_rect_2 = pygame.Rect(0, horizon_pos - 7, settings.WINDOW_WIDTH, 4)
            horizon_rect_3 = pygame.Rect(0, horizon_pos - 10, settings.WINDOW_WIDTH, 2)
            # Draw them
            pygame.draw.rect(self.surface, settings.COLORS["HORIZON_TOP"], horizon_rect_1)
            pygame.draw.rect(self.surface, settings.COLORS["HORIZON_TOP"], horizon_rect_2)
            pygame.draw.rect(self.surface, settings.COLORS["HORIZON_TOP"], horizon_rect_3)

            # Draw once more one horizon line for a nice look
            pygame.draw.line(self.surface, settings.COLORS["HORIZON"],
                             (0, horizon_pos), (settings.WINDOW_WIDTH, horizon_pos), 3)

        # Fill the screen in sea color, if the horizon isn't visible
        elif horizon_pos < 0:
            self.surface.fill(settings.COLORS["SEA"])
