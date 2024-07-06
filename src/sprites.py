import pygame
from pygame.math import Vector2 as vector


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
