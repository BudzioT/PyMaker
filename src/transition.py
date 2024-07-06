import pygame
from pygame.math import Vector2 as vector

from src.settings import settings


class Transition:
    """Transition between editor and the level"""
    def __init__(self, toggle_editor):
        """Initialize the transition"""
        # Get program's surface
        self.surface = pygame.display.get_surface()
        # Toggle the editor function
        self.toggle_editor = toggle_editor

        # Transition active flag
        self.active = False

        # Center of the transition
        self.center = (settings.WINDOW_WIDTH / 2, settings.WINDOW_HEIGHT / 2)
        # Radius of the transition circle
        self.radius = vector(self.center).magnitude()
        # Its border width
        self.border_width = 0
        # Direction of it
        self.direction = 1
        # The threshold
        self.threshold = self.radius + 100

    def display(self, delta_time):
        """Display the transition effect"""
        # Change size of the border by little, depending on the direction, increase or decrease it
        self.border_width += 1000 * delta_time * self.direction

        # If border exceeded the threshold, set the direction to the opposite one
        if self.border_width >= self.threshold:
            self.direction = -1

        # Draw the effect
        pygame.draw.circle(self.surface, "black", self.center, self.radius, int(self.border_width))
