import pygame.transform

from src.sprites import GenericSprite
from src.settings import settings


class Spikes(GenericSprite):
    """Spikes that damage the player"""
    def __init__(self, pos, assets, group):
        """Initialize the spikes"""
        super().__init__(pos, assets, group)


class Tooth(GenericSprite):
    """Tooth enemy, that can walk"""
    def __init__(self, pos, assets, group):
        """Initialize the tooth enemy"""
        # Get the frames, set the current frame
        self.frames = assets
        self.frame = 0

        # Direction of the enemy
        self.direction = "right"

        # Get the first frame of running
        surface = self.frames[f"run_{self.direction}"][self.frame]

        # Initialize generic sprite with first frame of run animation
        super().__init__(pos, surface, group)

        # Place the enemy on the ground
        self.rect.bottom = self.rect.top + settings.TILE_SIZE


class Shell(GenericSprite):
    """The shell enemy, that player can jump on"""
    def __init__(self, pos, assets, group, direction):
        """Initialize the shell"""
        # Animation frames (copy because it might need a flip, without a copy it would flip all the shells)
        self.frames = assets.copy()
        self.frame = 0

        # Direction of the shell
        self.direction = direction

        # If the direction is right, flip the assets
        if direction == "right":
            # Go through each of the animation type, get its image
            for animation_type, images in self.frames.items():
                # Check and flip all the images in this animation type
                self.frames[animation_type] = [pygame.transform.flip(image, True, False)
                                               for image in images]
        # Current state of the shell
        self.state = "idle"

        # Initialize the generic sprite with first frame of idle animation
        super().__init__(pos, self.frames[self.state][self.frame], group)

        # Place it on the ground
        self.rect.bottom = self.rect.top + settings.TILE_SIZE
