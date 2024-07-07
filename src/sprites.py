import pygame
from pygame.math import Vector2 as vector

from src.settings import settings


class GenericSprite(pygame.sprite.Sprite):
    """Generic, normal sprite"""
    def __init__(self, pos, surface, group):
        """Initialize the sprite"""
        super().__init__(group)
        # Get sprite image
        self.image = surface
        # Get the image rectangle and place it at the given position
        self.rect = self.image.get_rect(topleft=pos)


class Player(GenericSprite):
    """Game's player"""
    def __init__(self, pos, group):
        """Initialize the player"""
        super().__init__(pos, pygame.Surface((32, 64)), group)
        self.image.fill("red")

        # Player's direction
        self.direction = vector()
        # His position
        self.pos = vector(self.rect.topleft)
        # Speed
        self.speed = 300

    def update(self, delta_time):
        # Handle the input
        self._input()

        # Let the player move
        self._move(delta_time)

    def _input(self):
        """Check and handle the input"""
        # Get the pressed keys
        keys = pygame.key.get_pressed()

        # If player pressed right or D, set his direction to right
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
        # Move to the left
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
        # Otherwise stay in-place
        else:
            self.direction.x = 0

    def _move(self, delta_time):
        """Move the player"""
        # Update player's position
        self.pos += self.direction * self.speed * delta_time

        # Update player's rectangle, round it for the speed to count precisely
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))


class AnimatedSprite(GenericSprite):
    """An animated sprite"""
    def __init__(self, pos, assets, group):
        """Initialize the animated sprite"""
        # Get the animation surfaces
        self.frames = assets
        # Current frame
        self.frame = 0

        # Initialize the GenericSprite with the current frame
        super().__init__(pos, self.frames[self.frame], group)

    def update(self, delta_time):
        """Update the sprite"""
        # Animate it
        self.animate(delta_time)

    def animate(self, delta_time):
        """Animate the sprite"""
        # Increase the frame by the speed
        self.frame += settings.ANIMATION_SPEED * delta_time

        # If frame exceeds the frames limit, reset it
        if self.frame >= len(self.frames):
            self.frame = 0

        # Set the current frame as the image
        self.image = self.frames[int(self.frame)]


class Coin(AnimatedSprite):
    """Certain type of coin"""
    def __init__(self, pos, assets, group, coin_type):
        """Initialize the coin"""
        super().__init__(pos, assets, group)

        # Get the coin type
        self.coin_type = coin_type

        # Update the rectangle to proper position (center)
        self.rect = self.image.get_rect(center=pos)
