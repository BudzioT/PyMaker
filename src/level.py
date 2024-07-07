import sys

import pygame
from pygame.math import Vector2 as vector

from src.settings import settings
from src.utilities import utilities
from src.sprites import GenericSprite, Player, AnimatedSprite, Coin, Block
from src.particle import Particle
from src.enemies import Spikes, Tooth, Shell
from src.camera import CameraGroup


class Level:
    """The game's level class"""
    def __init__(self, grid, switch, assets):
        """Initialize the game's level"""
        # Get the main surface
        self.surface = pygame.display.get_surface()

        # Switch between the editor and level
        self.switch = switch

        # Group with all the sprites
        self.sprites = CameraGroup()
        # Only coin sprites
        self.coin_sprites = pygame.sprite.Group()
        # Sprites that deal damage
        self.attack_sprites = pygame.sprite.Group()
        # Sprites that can collide
        self.collision_sprites = pygame.sprite.Group()
        # Shell sprites
        self.shell_sprites = pygame.sprite.Group()

        # Particle surface assets
        self.particle_assets = assets["particle"]

        # Build the level based off the grid
        self._build_level(grid, assets)

    def run(self, delta_time):
        """Run the game level"""
        # Handle events
        self._get_events()

        # Update positions
        self._update_pos(delta_time)

        # Update the surface
        self._update_surface()

    def _get_events(self):
        """Get and handle the events"""
        # Go through every event
        for event in pygame.event.get():
            # If user wants to quit, free the pygame resources and exit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # If user clicks escape, switch to the editor
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch()

    def _update_pos(self, delta_time):
        """Update positions of elements"""
        # Update the player's position
        self.sprites.update(delta_time)

        # Make the player collect coins
        self._collect_coins()

    def _update_surface(self):
        """Update the surface"""
        # Draw the sky
        self.surface.fill(settings.COLORS["SKY"])
        # Draw all the sprites
        # self.sprites.draw(self.surface)
        self.sprites.custom_draw(self.player)

    def _build_level(self, grid, assets):
        """Build the level based off the grid using the given assets"""
        # Go through every single one of grid layers
        for layer_name, layer in grid.items():
            # Check all the layer placements
            for pos, data in layer.items():
                # If this layer is terrain, create a sprite with land at saved position
                if layer_name == "terrain":
                    GenericSprite(pos, assets["land"][data], [self.sprites, self.collision_sprites])

                # Check if layer is water one
                if layer_name == "water":
                    # If the tile is top one, create the water top tile with animation
                    if data == "top":
                        AnimatedSprite(pos, assets["water_top"], self.sprites, settings.LAYERS_DEPTH["water"])
                    # Otherwise create the bottom, plain one
                    else:
                        GenericSprite(pos, assets["water_bottom"], self.sprites, settings.LAYERS_DEPTH["water"])

                # If layer's ID was 0, place the player
                if data == 0:
                    self.player = Player(pos, assets["player"], self.sprites, self.collision_sprites)

                # Generate the specific coins
                # Gold
                elif data == 4:
                    Coin(pos, assets["gold_coin"], [self.sprites, self.coin_sprites], "gold")
                # Silver
                elif data == 5:
                    Coin(pos, assets["silver_coin"], [self.sprites, self.coin_sprites], "silver")
                # Diamond
                elif data == 6:
                    Coin(pos, assets["diamond_coin"], [self.sprites, self.coin_sprites], "diamond")

                # Enemies
                # Spikes
                elif data == 7:
                    Spikes(pos, assets["spikes"], [self.sprites, self.attack_sprites])
                # Tooth enemy
                elif data == 8:
                    Tooth(pos, assets["tooth"], [self.sprites, self.attack_sprites])
                # Shell in the left direction (it isn't in attack sprites, because player can jump on it)
                elif data == 9:
                    Shell(pos, assets["shell"], [self.sprites, self.collision_sprites, self.shell_sprites],
                          "left", assets["pearl"])
                # Shell in the right direction
                elif data == 10:
                    Shell(pos, assets["shell"], [self.sprites, self.collision_sprites, self.shell_sprites],
                          "right", assets["pearl"])

                # Palms
                # Small palm foreground
                elif data == 11:
                    AnimatedSprite(pos, assets["palms"]["small_fg"], self.sprites)
                    # Create a block that player can stand on (player should be able to stand on leafs)
                    Block(pos, (77, 50), self.collision_sprites)
                # Large palm foreground
                elif data == 12:
                    AnimatedSprite(pos, assets["palms"]["large_fg"], self.sprites)
                    Block(pos, (77, 50), self.collision_sprites)
                # Left foreground
                elif data == 13:
                    AnimatedSprite(pos, assets["palms"]["left_fg"], self.sprites)
                    Block(pos, (77, 50), self.collision_sprites)
                # Right foreground
                elif data == 14:
                    AnimatedSprite(pos, assets["palms"]["right_fg"], self.sprites)
                    Block(pos + vector(50, 0), (77, 50), self.collision_sprites)

                # Small palm background
                elif data == 15:
                    AnimatedSprite(pos, assets["palms"]["small_bg"], self.sprites, settings.LAYERS_DEPTH["bg"])
                # Large background
                elif data == 16:
                    AnimatedSprite(pos, assets["palms"]["large_bg"], self.sprites, settings.LAYERS_DEPTH["bg"])
                # Left background
                elif data == 17:
                    AnimatedSprite(pos, assets["palms"]["left_bg"], self.sprites, settings.LAYERS_DEPTH["bg"])
                # Right background
                elif data == 18:
                    AnimatedSprite(pos, assets["palms"]["right_bg"], self.sprites, settings.LAYERS_DEPTH["bg"])

            # Go through each of the shell sprites
            for shell in self.shell_sprites:
                # Save the player in it
                shell.player = self.player

    def _collect_coins(self):
        """Collect the coins by the player"""
        # Get the collided coins with the player, delete them
        collided_coins = pygame.sprite.spritecollide(self.player, self.coin_sprites, True)

        # Make some particles
        for coin in collided_coins:
            Particle(coin.rect.center, self.particle_assets, self.sprites)
