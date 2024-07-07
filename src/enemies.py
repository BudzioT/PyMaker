from random import choice

import pygame.transform
from pygame.math import Vector2 as vector

from src.sprites import GenericSprite
from src.settings import settings
from src.timer import Timer


class Spikes(GenericSprite):
    """Spikes that damage the player"""
    def __init__(self, pos, assets, group):
        """Initialize the spikes"""
        super().__init__(pos, assets, group)


class Tooth(GenericSprite):
    """Tooth enemy, that can walk"""
    def __init__(self, pos, assets, group, collision_sprites):
        """Initialize the tooth enemy"""
        # Get the frames, set the current frame
        self.frames = assets
        self.frame = 0

        # Direction of the enemy
        self.orientation = "right"

        # Sprites that he can collide with
        self.collision_sprites = collision_sprites

        # Get the first frame of running
        surface = self.frames[f"run_{self.orientation}"][self.frame]

        # Initialize generic sprite with first frame of run animation
        super().__init__(pos, surface, group)

        # Place the enemy on the ground
        self.rect.bottom = self.rect.top + settings.TILE_SIZE

        # Set his direction to random one
        self.direction = vector(choice((1, -1)), 0)
        # Set his position and speed
        self.pos = vector(self.rect.topleft)
        self.speed = 120


class Shell(GenericSprite):
    """The shell enemy, that player can jump on"""
    def __init__(self, pos, assets, group, orientation, pearl_surface, damage_group):
        """Initialize the shell"""
        # Animation frames (copy because it might need a flip, without a copy it would flip all the shells)
        self.frames = assets.copy()
        self.frame = 0

        # Direction of the shell
        self.orientation = orientation

        # If the direction is right, flip the assets
        if orientation == "right":
            # Go through each of the animation type, get its image
            for animation_type, images in self.frames.items():
                # Check and flip all the images in this animation type
                self.frames[animation_type] = [pygame.transform.flip(image, True, False)
                                               for image in images]
        # Current state of the shell
        self.state = "idle"

        # Pearl bullet surface
        self.pearl_surface = pearl_surface
        # Shoot flag
        self.shoot = False
        # Its cooldown
        self.shoot_cooldown = Timer(2000)
        # Damage sprite for making the pearl attack the player
        self.damage_sprites = damage_group

        # Initialize the generic sprite with first frame of idle animation
        super().__init__(pos, self.frames[self.state][self.frame], group)

        # Place it on the ground
        self.rect.bottom = self.rect.top + settings.TILE_SIZE

    def update(self, delta_time):
        """Update the shell"""
        # Animate the shell
        self._animate(delta_time)
        # Update it's state
        self._update_state()

        # Update the cooldown
        self.shoot_cooldown.update()

    def _animate(self, delta_time):
        """Animate the shell"""
        # Get the animation frames based off the shell state
        frames = self.frames[self.state]

        # Increase the frame
        self.frame += settings.ANIMATION_SPEED * delta_time
        # Ensure that it is in range
        if self.frame >= len(frames):
            self.frame = 0

            # If the shell already shot, turn on the cooldown
            if self.shoot:
                self.shoot_cooldown.start()
                # Set shoot flag to False
                self.shoot = False

        # Set the image to the current animation frame
        self.image = frames[int(self.frame)]

        # If the shell is on the shooting frame (second one), it is attacking, and it didn't shoot yet
        if int(self.frame) >= 2 and self.state == "attack" and not self.shoot:
            # If shell's direction is left, make the pearl direction left to
            if self.orientation == "left":
                pearl_direction = vector(-1, 0)
                # Get the pearl offset
                pearl_offset = (pearl_direction * 50) + vector(0, -10)
            # Otherwise make it right and take its offset
            else:
                pearl_direction = vector(1, 0)
                pearl_offset = (pearl_direction * 20) + vector(0, -10)

            # Turn on the shoot flag
            self.shoot = True
            # Create the pearl with specified direction, starting at the center of the shell
            Pearl(self.rect.center + pearl_offset, self.pearl_surface,
                  [self.damage_sprites, self.groups()[0]], pearl_direction)

    def _update_state(self):
        """Update the shell's state"""
        # If player is close enough to the shell
        if vector(self.player.rect.center).distance_to(vector(self.rect.center)) < 485:
            # If the shell can shoot, do set it's state to attack
            if not self.shoot_cooldown.active:
                self.state = "attack"

        # Otherwise just idle
        else:
            self.state = "idle"


class Pearl(GenericSprite):
    """Pearl projectile"""
    def __init__(self, pos, surface, group, direction):
        """Initialize the pearl"""
        super().__init__(pos, surface, group)

        # Pearl position
        self.pos = vector(self.rect.topleft)
        # Its direction and speed
        self.direction = direction
        self.speed = 150

        # Pearl duration time
        self.timer = Timer(7000)
        self.timer.start()

    def update(self, delta_time):
        """Update the pearl"""
        # Update position and the rectangle
        self.pos.x += self.direction.x * self.speed * delta_time
        self.rect.x = round(self.pos.x)

        # Update the timer
        self.timer.update()
        # If the timer passed, kill the pearl
        if not self.timer.active:
            self.kill()
