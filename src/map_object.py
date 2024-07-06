import pygame


class MapObject(pygame.sprite.Sprite):
    """Object that can be moved freely on the map"""
    def __init__(self, group):
        """Initialize the map object"""
        super().__init__(group)
        pass
