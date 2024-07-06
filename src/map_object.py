import pygame
from pygame.math import Vector2 as vector
from pygame.mouse import get_pos as mouse_pos

from src.settings import settings


class MapObject(pygame.sprite.Sprite):
    """Object that can be moved freely on the map"""
    def __init__(self, pos, frames, tile_id, origin, group):
        """Initialize the map object"""
        super().__init__(group)

        # Tile id
        self.tile_id = tile_id

        # Animation variables
        self.frames = frames
        self.frame = 0

        # Image of the object and its rectangle, center it around given position
        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect(center=pos)

        # Distance to the map's origin
        self.origin_distance = vector(self.rect.topleft) - origin
        # Mouse offset from the top left part of this object
        self.mouse_offset = vector()

        # Select flag
        self.selected = False

    def update_pos(self, origin):
        """Update position after panning"""
        # Update the top left position of the item
        self.rect.topleft = origin + self.origin_distance

    def update(self, delta_time):
        """Update the map object"""
        self._animate(delta_time)
        self.drag()

    def _animate(self, delta_time):
        """Animate the object"""
        # Increase the current frame
        self.frame += settings.ANIMATION_SPEED * delta_time

        # Don't allow the animation to go beyond number of frames
        if self.frame >= len(self.frames):
            self.frame = 0

        # Set it as the current image
        self.image = self.frames[int(self.frame)]
        # Update the object's rectangle, to stay always in the same position
        self.rect = self.image.get_rect(midbottom = self.rect.midbottom)

    def drag(self):
        """Drag the object"""
        if self.selected:
            self.rect.topleft = mouse_pos() - self.mouse_offset

    def prepare_drag(self):
        """Prepare the object before dragging it"""
        # Make it selected
        self.selected = True
        # Get the mouse offset from top left part of the object
        self.mouse_offset = vector(mouse_pos()) - vector(self.rect.topleft)

    def end_drag(self, origin):
        """End the drag"""
        # Unselect the object
        self.selected = False
        # Recalculate the distance to the map's origin
        self.origin_distance = vector(self.rect.topleft) - origin
