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

        # Go through each of sprite within this group
        for sprite in self:
            # Go through each possible layer depth value, starting from the most background ones
            for layer_depth in settings.LAYERS_DEPTH.values():
                # If layer position is right, handle the sprite drawing
                if sprite.pos_z == layer_depth:
                    # Get this sprite rectangle
                    rect = sprite.rect.copy()
                    # Apply offset to it
                    rect.center -= self.offset

                    # Blit this sprite
                    self.surface.blit(sprite.image, rect)
