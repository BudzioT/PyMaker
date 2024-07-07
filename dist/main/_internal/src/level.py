import os.path
import sys
from random import choice, randint

import pygame
from pygame.math import Vector2 as vector

from src.settings import settings
from src.utilities import utilities
from src.sprites import GenericSprite, Player, AnimatedSprite, Coin, Block, Cloud
from src.particle import Particle
from src.enemies import Spikes, Tooth, Shell
from src.camera import CameraGroup
from src.ui import UI


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

        # Game's user's interface
        self.ui = UI()

        # Particle surface assets
        self.particle_assets = assets["particle"]

        # Cloud surfaces
        self.cloud_surfaces = assets["clouds"]
        # Cloud appear timer
        self.cloud_timer = pygame.USEREVENT + 2
        pygame.time.set_timer(self.cloud_timer, 4000)

        # Load the sounds
        self.sounds = {
            "coin": pygame.mixer.Sound(os.path.join(settings.BASE_PATH, "../audio/coin.wav")),
            "hit": pygame.mixer.Sound(os.path.join(settings.BASE_PATH, "../audio/hit.wav")),
            "jump": pygame.mixer.Sound(os.path.join(settings.BASE_PATH, "../audio/jump.wav")),
        }
        # Lower the volumes
        for sound in self.sounds.values():
            sound.set_volume(0.2)

        # Build the level based off the grid
        self._build_level(grid, assets)

        # Level position limits
        self.level_limits = {
            "left": -settings.WINDOW_WIDTH,
            # Get the right-most stile
            "right": sorted(list(grid["terrain"].keys()), key=lambda pos: pos[0])[-1][0]
        }

        # Create some start clouds
        self._start_clouds()

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

            # If cloud appear cooldown has ended, spawn a new cloud
            if event.type == self.cloud_timer:
                self._create_clouds()

    def _update_pos(self, delta_time):
        """Update positions of elements"""
        # Update the player's position
        self.sprites.update(delta_time)

        # Check and handle player's damage
        self._damage()

        # Make the player collect coins
        self._collect_coins()

    def _update_surface(self):
        """Update the surface"""
        # Draw the sky
        self.surface.fill(settings.COLORS["SKY"])

        # Draw all the sprites
        self.sprites.custom_draw(self.player)

        # Display user's interface
        self.ui.display(self.player)

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
                    self.player = Player(pos, assets["player"], self.sprites, self.collision_sprites,
                                         self.sounds["jump"])
                # Set the horizon
                elif data == 1:
                    self.horizon_y = pos[1]
                    self.sprites.horizon_y = pos[1]

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
                    Tooth(pos, assets["tooth"], [self.sprites, self.attack_sprites], self.collision_sprites)
                # Shell in the left direction (it isn't in attack sprites, because player can jump on it)
                elif data == 9:
                    print(pos)
                    Shell(pos, assets["shell"], [self.sprites, self.collision_sprites, self.shell_sprites],
                          "left", assets["pearl"], self.attack_sprites)
                # Shell in the right direction
                elif data == 10:
                    print(pos)
                    Shell(pos, assets["shell"], [self.sprites, self.collision_sprites, self.shell_sprites],
                          "right", assets["pearl"], self.attack_sprites)

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

    def _create_clouds(self):
        """Create the clouds"""
        # Choose a random cloud surface
        surface = choice(self.cloud_surfaces)
        # Scale it times two randomly
        if randint(0,5) > 3:
            surface = pygame.transform.scale2x(surface)

        # Cloud random starting position (check if user placed any tile, if not set starting X position to 500)
        pos_x = self.level_limits["right"] + randint(100, 300) if self.level_limits["right"] else 500
        pos_y = self.horizon_y - randint(-20, 600)

        # Create the cloud
        Cloud((pos_x, pos_y), surface, self.sprites, self.level_limits["left"])

    def _start_clouds(self):
        """Create some clouds at start of the level"""
        # Create 30 clouds
        for cloud_num in range(30):
            # Randomly choose a cloud surface
            surface = choice(self.cloud_surfaces)
            # Sometimes scale it up
            if randint(0, 5) > 3:
                surface = pygame.transform.scale2x(surface)

            # Get the random positions at the screen, depending on, if there was any tile placed
            if self.level_limits["right"]:
                pos_x = randint(self.level_limits["left"], self.level_limits["right"])
            else:
                pos_x = randint(self.level_limits["left"], 500)
            pos_y = self.horizon_y - randint(-20, 600)

            # Create the cloud
            Cloud((pos_x, pos_y), surface, self.sprites, self.level_limits["left"])

    def _collect_coins(self):
        """Collect the coins by the player"""
        # Get the collided coins with the player, delete them
        collided_coins = pygame.sprite.spritecollide(self.player, self.coin_sprites, True)

        # If there was any collision
        if collided_coins:
            # Play the sound
            self.sounds["coin"].play()

        # Go through each collided coin
        for coin in collided_coins:
            # Add it to the player's total coin amount, based off coin's type
            if coin.coin_type == "gold":
                self.player.coins += 1
            elif coin.coin_type == "silver":
                self.player.coins += 2
            elif coin.coin_type == "diamond":
                self.player.coins += 5

            # Make some particles
            Particle(coin.rect.center, self.particle_assets, self.sprites)

    def _damage(self):
        """Damage the player if needed"""
        # Check for collisions with attack sprites and the player
        collisions = pygame.sprite.spritecollide(self.player, self.attack_sprites, False,
                                                 pygame.sprite.collide_mask)
        # If there is one, damage the player
        if collisions:
            self.player.damage()
            # Decrease his health
            self.player.health -= 1
            # Play the damage sound
            self.sounds["hit"].play()

        if self.player.health <= 0:
            self.switch()
