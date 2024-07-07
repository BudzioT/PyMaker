import pygame
from pygame.math import Vector2 as vector

from src.settings import settings
from src.timer import Timer


class GenericSprite(pygame.sprite.Sprite):
    """Generic, normal sprite"""
    def __init__(self, pos, surface, group, pos_z=settings.LAYERS_DEPTH["main"]):
        """Initialize the sprite"""
        super().__init__(group)
        # Get sprite image
        self.image = surface
        # Get the image rectangle and place it at the given position
        self.rect = self.image.get_rect(topleft=pos)

        # Save the depth position
        self.pos_z = pos_z


class Player(GenericSprite):
    """Game's player"""
    def __init__(self, pos, assets, group, collision_sprites):
        """Initialize the player"""
        # Animation variables
        self.frames = assets
        self.frame = 0
        # Player's current state
        self.state = "idle"
        # His orientation
        self.orientation = "right"

        # Get the player's current animation image based off the state and orientation
        surface = self.frames[f"{self.state}_{self.orientation}"][self.frame]
        # Initialize the parent class with it
        super().__init__(pos, surface, group)

        # Create mask
        self.mask = pygame.mask.from_surface(self.image)

        # Player's direction
        self.direction = vector()
        # His position
        self.pos = vector(self.rect.center)
        # Speed
        self.speed = 300

        # Gravity
        self.gravity = 4
        # Player on floor flag
        self.floor = False

        # Sprites that collide with player
        self.collision_sprites = collision_sprites
        # Player's hitboxes
        self.hitbox = self.rect.inflate(-50, 0)

        # Player's invincibility time
        self.dodge_time = Timer(300)

    def update(self, delta_time):
        # Handle the input
        self._input()

        # Apply gravity to the player
        self._apply_gravity(delta_time)

        # Update the invincibility timer
        self.dodge_time.update()

        # Let the player move
        self._move(delta_time)
        # Save the floor if player is standing on one
        self._check_floor()

        # Check his state and update it
        self._update_state()
        # Animate him
        self._animate(delta_time)

    def _input(self):
        """Check and handle the input"""
        # Get the pressed keys
        keys = pygame.key.get_pressed()

        # If player pressed right or D, set his direction to right
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            # Set his orientation to right too
            self.orientation = "right"
        # Move to the left
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            # Set the orientation to left
            self.orientation = "left"
        # Otherwise stay in-place
        else:
            self.direction.x = 0

        # If player wants to jump and is on the floor
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.floor:
            # Increase the direction to the top
            self.direction.y = -2

    def _move(self, delta_time):
        """Move the player"""
        # Update player's horizontal position
        self.pos.x += self.direction.x * self.speed * delta_time
        # Move the hitboxes, round for float precision
        self.hitbox.centerx = round(self.pos.x)
        # Update the player's rect based off hitboxes
        self.rect.centerx = self.hitbox.centerx

        # Check for horizontal collisions
        self._collision("horizontal")

        # Handle player's vertical movement
        self.pos.y += self.direction.y * self.speed * delta_time
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery

        # Check for vertical collisions
        self._collision("vertical")

    def _collision(self, direction):
        """Check for collisions and handle them"""
        # Check all the collisions sprites
        for sprite in self.collision_sprites:
            # Find out if player collides with this sprite
            if sprite.rect.colliderect(self.hitbox):
                # If he collides in horizontal direction, handle it
                if direction == "horizontal":
                    # If player was moving right, hug him to the left part of collider
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.rect.left
                    # If player was moving left, hug him to the right side
                    elif self.direction.x < 0:
                        self.hitbox.left = sprite.rect.right

                    # Update player's rectangle based off hitboxes
                    self.rect.centerx = self.hitbox.centerx
                    # Update player's position
                    self.pos.x = self.hitbox.centerx

                # Handle vertical collisions
                else:
                    # If player moved up, don't allow him to pass through the top block
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.rect.bottom
                    # If player was falling, place him on the ground
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.rect.top

                    # Update rectangle based off hitboxes
                    self.rect.centery = self.hitbox.centery
                    # Update the position
                    self.pos.y = self.hitbox.centery

                    # Reset the gravity force applied to the player
                    self.direction.y = 0

    def _apply_gravity(self, delta_time):
        """Apply gravity to the player"""
        # Apply gravity to the player's direction
        self.direction.y += self.gravity * delta_time
        # Make the player fall
        self.rect.y += self.direction.y

    def _check_floor(self):
        """Check if player is on the floor"""
        # Get the floor rect of player (bottom part of him)
        floor_rect = pygame.Rect(self.hitbox.bottomleft, (self.hitbox.width, 2))

        # Get all the collision sprites, that he is on
        floor_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.colliderect(floor_rect)]
        # Set the floor flag if there was any floor collision
        self.floor = True if floor_sprites else False

    def _animate(self, delta_time):
        """Animate the player"""
        # Get the current state animation frames
        frames = self.frames[f"{self.state}_{self.orientation}"]

        # Increase the current frame
        self.frame += settings.ANIMATION_SPEED * delta_time

        # Check and reset the frame if it was the last one
        if self.frame >= len(frames):
            self.frame = 0

        # Update the current image
        self.image = frames[int(self.frame)]

        # Update the mask
        self.mask = pygame.mask.from_surface(self.image)

        # If player is invincible
        if self.dodge_time.active:
            surface = self.mask.to_surface()
            surface.set_colorkey("black")
            self.image = surface

    def _update_state(self):
        """Get the state that player's in"""
        # If player's direction goes up, set his state to jump
        if self.direction.y < 0:
            self.state = "jump"
        # If player's direction pushes him down, set his state to fall
        elif self.direction.y > 0.8:
            self.state = "fall"

        # Otherwise check the horizontal states
        else:
            # If player's moving set the state to run
            if self.direction.x != 0:
                self.state = "run"
            # Otherwise set it to idle
            else:
                self.state = "idle"

    def damage(self):
        """Damage the player"""
        if not self.dodge_time.active:
            self.dodge_time.start()
            self.direction.y -= 1.5


class AnimatedSprite(GenericSprite):
    """An animated sprite"""
    def __init__(self, pos, assets, group, pos_z=settings.LAYERS_DEPTH["main"]):
        """Initialize the animated sprite"""
        # Get the animation surfaces
        self.frames = assets
        # Current frame
        self.frame = 0

        # Initialize the GenericSprite with the current frame
        super().__init__(pos, self.frames[self.frame], group, pos_z)

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


class Block(GenericSprite):
    """Block that player can walk on"""
    def __init__(self, pos, size, group):
        """Initialize the block"""
        # Create the block's surface
        surface = pygame.Surface(size)

        # Initialize the parent class
        super().__init__(pos, surface, group)


class Coin(AnimatedSprite):
    """Certain type of coin"""
    def __init__(self, pos, assets, group, coin_type):
        """Initialize the coin"""
        super().__init__(pos, assets, group)

        # Get the coin type
        self.coin_type = coin_type

        # Update the rectangle to proper position (center)
        self.rect = self.image.get_rect(center=pos)
